from src.llm import call_llm
import json

ROUTE_TYPES = ["KNOWLEDGE_BASE", "TICKET_LOOKUP", "ACCOUNT_LOOKUP", "AMBIGUOUS", "UNSUPPORTED"]

ROUTER_PROMPT = """
You are a query router for a SaaS support assistant.
Classify the user query into exactly one of these routes:

- KNOWLEDGE_BASE: Questions about refund policy, account upgrades, API rate limits, security practices, or integration setup. ONLY use this if the topic clearly matches one of these 5 areas.
- TICKET_LOOKUP: Query references a specific ticket ID (like T-2001) OR asks about ticket lists, ticket status, or ticket assignments. If no ticket ID or clear ticket context is given, do NOT use this route.
- ACCOUNT_LOOKUP: Query references a specific customer or company name and asks about their plan, renewal date, health score, or open tickets.
- AMBIGUOUS: The query is too vague to route confidently. Use this when a ticket is mentioned but no ID is given, or a customer is mentioned but no name is given. When in doubt, use AMBIGUOUS.
- UNSUPPORTED: The information requested is not available in refund policy, account upgrades, API rate limits, security practices, integration setup, ticket data, or account data. Use this for compliance questions (HIPAA, GDPR), legal questions, deployment questions, or anything outside the above topics.

IMPORTANT RULES:
- "Check that ticket" with no ID = AMBIGUOUS
- "What is going on with Acme?" with no specific field = AMBIGUOUS  
- HIPAA, GDPR, legal, on-premise deployment = UNSUPPORTED
- Only use KNOWLEDGE_BASE for the 5 documented topics listed above

Respond ONLY with raw JSON, no markdown, no code fences:
{{
  "route": "<ONE OF THE 5 ROUTES>",
  "confidence": <float between 0 and 1>,
  "reason": "<one sentence explanation>"
}}

User query: {query}
"""

def route_query(query: str) -> dict:
    prompt = ROUTER_PROMPT.format(query=query)
    raw = call_llm(prompt).strip()

    # Strip markdown code fences just in case
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)

    # Safety check
    if result.get("route") not in ROUTE_TYPES:
        result["route"] = "UNSUPPORTED"
        result["confidence"] = 0.5

    return result