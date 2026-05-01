from src.account_lookup import lookup_accounts

queries = [
    "What plan is Acme Corp on?",
    "When does Delta Retail renew?",
    "Which accounts have low health scores?",
    "Which customers have open tickets?",
]

for q in queries:
    result = lookup_accounts(q)
    print(f"Q: {q}")
    print(f"→ Filter: {result['filter_used']}")
    print(f"→ Found {len(result['matched_accounts'])} account(s):")
    for a in result["matched_accounts"]:
        print(f"   {a['customer_name']} | plan: {a['plan']} | renews: {a['renewal_date']} | health: {a['health_score']} | open tickets: {a['open_ticket_count']}")
    print()