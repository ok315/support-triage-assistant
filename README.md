# 🤖 AI-Powered Support Triage Assistant

An intelligent support triage system that classifies incoming queries, retrieves answers from the correct data source, and returns structured decision outputs — built for a SaaS support team.

---

## 📌 Overview

This assistant classifies every incoming support query into one of five route types before generating a response:

| Route | Trigger |
|---|---|
| `KNOWLEDGE_BASE` | Policy or informational question |
| `TICKET_LOOKUP` | Query about a specific ticket or ticket list |
| `ACCOUNT_LOOKUP` | Query about a customer or account |
| `AMBIGUOUS` | Insufficient context to route confidently |
| `UNSUPPORTED` | Information not available in any provided source |

Every response includes both a **human-readable answer** and a **structured decision object** explaining how the system handled the request.

---

## 🗂️ Project Structure

```
support-triage-assistant/
├── data/
│   ├── knowledge_base/
│   │   ├── refund_policy.md
│   │   ├── account_upgrade.md
│   │   ├── api_rate_limits.md
│   │   ├── security_practices.md
│   │   └── integration_setup.md
│   ├── accounts.json
│   └── tickets.json
├── src/
│   ├── __init__.py
│   ├── account_lookup.py      # Account data retrieval and filtering
│   ├── kb_lookup.py           # RAG pipeline for knowledge base
│   ├── llm.py                 # LLM client and prompt logic
│   ├── router.py              # Query classification and routing
│   └── ticket_lookup.py       # Ticket data retrieval and filtering
├── .env                       # Your local environment variables (not committed)
├── .env.example               # Environment variable template
├── .gitignore
├── main.py                    # CLI entry point
├── requirements.txt
└── test_llm.py                # LLM connectivity test
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ok315/support-triage-assistant.git
cd support-triage-assistant
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and add your API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Verify LLM Connectivity (Optional)

```bash
python test_llm.py
```

---

## 🚀 Running the System

### Interactive CLI Mode

```bash
python main.py
```

The assistant will prompt you to enter queries interactively. Type `exit` or `quit` to stop.

### Single Query Mode

```bash
python main.py --query "What is your refund policy?"
```

---

## 💬 Example Queries

### Knowledge Base

```
What is your refund policy?
How do I upgrade my plan?
What are the API rate limits?
How do I set up an integration?
```

### Ticket Lookup

```
What is the status of ticket T-2001?
Who is assigned to T-2003?
Which urgent tickets are still open?
Which tickets are currently unassigned?
```

### Account Lookup

```
What plan is Acme Corp on?
When does Delta Retail renew?
Which accounts have low health scores?
Which customers have open tickets and a low health score?
```

### Support Priority Triage

```
Which issues should the support team handle first today?
```

### Ambiguous (triggers clarification)

```
Check that ticket for me
What is going on with Acme?
Can you look at the integration issue?
```

### Unsupported (gracefully refused)

```
Do you support on-premise deployment?
What are the legal policies for Germany?
Are you HIPAA compliant?
```

---

## 📤 Structured Decision Output

Every response returns a structured decision object alongside the human-readable answer:

```json
{
  "route": "TICKET_LOOKUP",
  "confidence": 0.92,
  "used_sources": ["tickets.json"],
  "used_tools": ["ticket_lookup"],
  "needs_clarification": false,
  "final_answer": "Ticket T-2002 is in progress, assigned to Hassan."
}
```

```json
{
  "route": "KNOWLEDGE_BASE",
  "confidence": 0.85,
  "used_sources": ["refund_policy.md"],
  "used_tools": [],
  "needs_clarification": false,
  "final_answer": "Annual plans are partially refundable within 7 days of payment."
}
```

```json
{
  "route": "AMBIGUOUS",
  "confidence": 0.45,
  "used_sources": [],
  "used_tools": [],
  "needs_clarification": true,
  "final_answer": "Could you clarify which ticket you're referring to? Please provide a ticket ID or customer name."
}
```

---

## 🧠 How It Works

### 1. Query Routing (`src/router.py`)
Every query is classified before any answer is generated. The router uses the LLM to assign one of the five route types along with a confidence score.

### 2. Knowledge Base Retrieval (`src/kb_lookup.py`)
Uses a lightweight RAG pipeline — documents are chunked, embedded, and searched by semantic similarity. Answers are grounded in retrieved context only, and source documents are cited.

### 3. Ticket Lookup (`src/ticket_lookup.py`)
Parses and filters `tickets.json` based on ticket IDs, status, priority, or assignment. Supports both single-record and list-based queries.

### 4. Account Lookup (`src/account_lookup.py`)
Parses and filters `accounts.json` based on customer name, health score, plan type, or renewal date. Supports cross-field filtering (e.g., low health + open tickets).

### 5. Support Priority Triage
When asked which issues to handle first, the system analyzes both `tickets.json` and `accounts.json` together and produces a ranked shortlist. Ranking weighs ticket priority, customer tier, account health score, ticket age, and open ticket count.

### 6. Ambiguity Handling
Queries that cannot be routed with sufficient confidence are classified as `AMBIGUOUS`. The system asks a targeted clarifying question rather than guessing.

### 7. Unsupported Refusal
If the requested information is not present in any knowledge base document or data file, the system classifies the query as `UNSUPPORTED` and informs the user — it never fabricates an answer.

---

## 📦 Dependencies

Key libraries used (see `requirements.txt` for full list):

- `openai` — LLM API client
- `faiss-cpu` — Vector similarity search for RAG
- `sentence-transformers` — Text embeddings
- `python-dotenv` — Environment variable management

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI (or compatible) API key |

See `.env.example` for the full template.

---

## 📝 Notes

- The assistant **never invents answers**. All responses are grounded in the provided data sources.
- Knowledge base retrieval cites the specific document(s) used.
- Ticket and account lookups operate directly on the provided JSON files — no database required.
- The system is designed to be extended: new route types or data sources can be added by updating the router and adding a corresponding lookup module.