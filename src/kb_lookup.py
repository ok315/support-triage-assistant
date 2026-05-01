import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

KB_PATH = "data/knowledge_base"

def load_documents():
    """Load all .md files and split into chunks with source tracking."""
    chunks = []
    for filename in os.listdir(KB_PATH):
        if filename.endswith(".md"):
            filepath = os.path.join(KB_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            # Split into paragraphs as chunks
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
            for para in paragraphs:
                chunks.append({
                    "text": para,
                    "source": filename
                })
    return chunks

def build_index(chunks):
    """Embed all chunks and build a FAISS index."""
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)  # normalize

    index = faiss.IndexFlatIP(embeddings.shape[1])  # Inner product = cosine similarity
    index.add(embeddings)
    return index, embeddings

# Build once at import time
_chunks = load_documents()
_index, _embeddings = build_index(_chunks)

def retrieve(query: str, top_k: int = 3) -> list[dict]:
    """Return top_k most relevant chunks for a query."""
    query_vec = model.encode([query], convert_to_numpy=True)
    query_vec = query_vec / np.linalg.norm(query_vec)

    scores, indices = _index.search(query_vec, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        results.append({
            "text": _chunks[idx]["text"],
            "source": _chunks[idx]["source"],
            "score": round(float(score), 4)
        })
    return results

def answer_from_kb(query: str, call_llm) -> dict:
    """Retrieve context and generate an answer using the LLM."""
    top_chunks = retrieve(query)

    sources = list(set(c["source"] for c in top_chunks))
    context = "\n\n---\n\n".join(c["text"] for c in top_chunks)

    prompt = f"""You are a SaaS support assistant. Answer the user's question using ONLY the context below.
If the answer is not in the context, say you don't have that information.

Context:
{context}

User question: {query}

Answer clearly and concisely."""

    answer = call_llm(prompt)

    return {
        "final_answer": answer,
        "used_sources": sources
    }