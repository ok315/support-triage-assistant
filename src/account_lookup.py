import json
import os

ACCOUNTS_PATH = os.path.join("data", "accounts.json")

def load_accounts():
    with open(ACCOUNTS_PATH, "r") as f:
        return json.load(f)

def lookup_accounts(query: str) -> dict:
    accounts = load_accounts()
    query_lower = query.lower()

    # 1. Specific customer name lookup
    for account in accounts:
        if account["customer_name"].lower() in query_lower:
            return {
                "matched_accounts": [account],
                "filter_used": f"customer_name = {account['customer_name']}"
            }

    # 2. Low health score (below 50)
    if "low health" in query_lower or "unhealthy" in query_lower or "health score" in query_lower:
        match = [a for a in accounts if a["health_score"] < 50]
        match.sort(key=lambda x: x["health_score"])
        return {"matched_accounts": match, "filter_used": "health_score < 50"}

    # 3. Accounts with open tickets
    if "open ticket" in query_lower:
        match = [a for a in accounts if a["open_ticket_count"] > 0]
        match.sort(key=lambda x: x["open_ticket_count"], reverse=True)
        return {"matched_accounts": match, "filter_used": "open_ticket_count > 0"}

    # 4. Low health AND open tickets combined
    if "low health" in query_lower and "open ticket" in query_lower:
        match = [a for a in accounts if a["health_score"] < 50 and a["open_ticket_count"] > 0]
        match.sort(key=lambda x: x["health_score"])
        return {"matched_accounts": match, "filter_used": "health_score < 50 AND open_ticket_count > 0"}

    # 5. By plan type
    for plan in ["enterprise", "pro", "basic"]:
        if plan in query_lower:
            match = [a for a in accounts if a["plan"] == plan]
            return {"matched_accounts": match, "filter_used": f"plan = {plan}"}

    # 6. Renewal date queries
    if "renew" in query_lower or "renewal" in query_lower or "expire" in query_lower:
        match = sorted(accounts, key=lambda x: x["renewal_date"])
        return {"matched_accounts": match, "filter_used": "sorted by renewal_date ascending"}

    # Fallback — return all accounts
    return {"matched_accounts": accounts, "filter_used": "all accounts"}