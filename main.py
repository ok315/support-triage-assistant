import json
from src.router import route_query
from src.llm import call_llm
from src.ticket_lookup import lookup_tickets
from src.account_lookup import lookup_accounts
from src.kb_lookup import answer_from_kb

TRIAGE_KEYWORDS = ["triage", "first today", "handle first", "priority order", "who should we help"]

def build_decision(route, confidence, sources, tools, needs_clarification, answer):
    return {
        "route": route,
        "confidence": confidence,
        "used_sources": sources,
        "used_tools": tools,
        "needs_clarification": needs_clarification,
        "final_answer": answer
    }

def format_tickets(tickets):
    if not tickets:
        return "No matching tickets found."
    lines = []
    for t in tickets:
        lines.append(
            f"  [{t['ticket_id']}] {t['customer_name']} | "
            f"Status: {t['status']} | Priority: {t['priority']} | "
            f"Assigned: {t.get('assigned_to', 'Unassigned')}"
        )
    return "\n".join(lines)

def format_accounts(accounts):
    if not accounts:
        return "No matching accounts found."
    lines = []
    for a in accounts:
        lines.append(
            f"  {a['customer_name']} | Plan: {a['plan']} | "
            f"Health: {a['health_score']} | "
            f"Renewal: {a['renewal_date']} | "
            f"Open Tickets: {a['open_ticket_count']}"
        )
    return "\n".join(lines)

def run_triage():
    """Rank support issues by combining ticket + account data."""
    from src.ticket_lookup import load_tickets
    from src.account_lookup import load_accounts

    tickets = load_tickets()
    accounts = load_accounts()

    # Build account lookup map by customer name
    account_map = {a["customer_name"]: a for a in accounts}

    PRIORITY_SCORE = {"urgent": 4, "high": 3, "medium": 2, "low": 1}
    TIER_SCORE = {"enterprise": 3, "pro": 2, "basic": 1}

    scored = []
    for t in tickets:
        if t["status"] == "resolved":
            continue  # skip resolved tickets

        account = account_map.get(t["customer_name"], {})
        health = account.get("health_score", 100)
        tier = account.get("plan", "basic")
        open_count = account.get("open_ticket_count", 0)

        score = 0
        score += PRIORITY_SCORE.get(t["priority"], 0) * 3   # priority is most important
        score += TIER_SCORE.get(tier, 1) * 2                # tier is second
        score += (100 - health) / 20                         # lower health = higher score
        score += min(open_count, 5) * 0.5                    # more open tickets = slightly higher

        scored.append({
            "ticket": t,
            "account": account,
            "score": round(score, 2),
            "tier": tier,
            "health": health
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:5]

    lines = ["🚨 Support Triage — Top Issues to Handle First:\n"]
    for i, item in enumerate(top, 1):
        t = item["ticket"]
        lines.append(
            f"{i}. [{t['ticket_id']}] {t['customer_name']} "
            f"(Score: {item['score']})\n"
            f"   Priority: {t['priority']} | Plan: {item['tier']} | "
            f"Health: {item['health']} | Status: {t['status']}\n"
            f"   Reason: {t['priority'].capitalize()} priority ticket for a "
            f"{item['tier']} customer with health score {item['health']}."
        )

    return "\n".join(lines)

def handle_query(query: str) -> dict:
    # Check for triage intent first
    if any(k in query.lower() for k in TRIAGE_KEYWORDS):
        answer = run_triage()
        return build_decision(
            route="TICKET_LOOKUP",
            confidence=1.0,
            sources=["tickets.json", "accounts.json"],
            tools=["ticket_lookup", "account_lookup"],
            needs_clarification=False,
            answer=answer
        )

    # Route the query
    routing = route_query(query)
    route = routing["route"]
    confidence = routing["confidence"]

    # --- KNOWLEDGE BASE ---
    if route == "KNOWLEDGE_BASE":
        result = answer_from_kb(query, call_llm)
        return build_decision(
            route=route,
            confidence=confidence,
            sources=result["used_sources"],
            tools=[],
            needs_clarification=False,
            answer=result["final_answer"]
        )

    # --- TICKET LOOKUP ---
    elif route == "TICKET_LOOKUP":
        result = lookup_tickets(query)
        tickets = result["matched_tickets"]
        answer = format_tickets(tickets)
        return build_decision(
            route=route,
            confidence=confidence,
            sources=["tickets.json"],
            tools=["ticket_lookup"],
            needs_clarification=False,
            answer=answer
        )

    # --- ACCOUNT LOOKUP ---
    elif route == "ACCOUNT_LOOKUP":
        result = lookup_accounts(query)
        accounts = result["matched_accounts"]
        answer = format_accounts(accounts)
        return build_decision(
            route=route,
            confidence=confidence,
            sources=["accounts.json"],
            tools=["account_lookup"],
            needs_clarification=False,
            answer=answer
        )

    # --- AMBIGUOUS ---
    elif route == "AMBIGUOUS":
        clarification = (
            "I need a bit more information to help you. "
            "Could you provide a specific ticket ID (e.g. T-2001), "
            "a customer name, or clarify what you're looking for?"
        )
        return build_decision(
            route=route,
            confidence=confidence,
            sources=[],
            tools=[],
            needs_clarification=True,
            answer=clarification
        )

    # --- UNSUPPORTED ---
    else:
        return build_decision(
            route=route,
            confidence=confidence,
            sources=[],
            tools=[],
            needs_clarification=False,
            answer="I'm sorry, that information is not available in my knowledge base or data sources."
        )

def main():
    print("=" * 55)
    print("  🤖 Support Triage Assistant  ")
    print("  Type 'exit' to quit          ")
    print("=" * 55)

    while True:
        print()
        query = input("You: ").strip()
        if not query:
            continue
        if query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        result = handle_query(query)

        print("\n--- Answer ---")
        print(result["final_answer"])
        print("\n--- Decision Object ---")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()