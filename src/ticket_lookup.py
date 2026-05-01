import json
import os

TICKETS_PATH = os.path.join("data", "tickets.json")

def load_tickets():
    with open(TICKETS_PATH, "r") as f:
        return json.load(f)

def lookup_tickets(query: str) -> dict:
    tickets = load_tickets()
    query_lower = query.lower()

    # 1. Specific ticket ID lookup (e.g. T-2003)
    for word in query.split():
        word_clean = word.strip("?.,").upper()
        if word_clean.startswith("T-"):
            match = [t for t in tickets if t["ticket_id"] == word_clean]
            if match:
                return {
                    "matched_tickets": match,
                    "filter_used": f"ticket_id = {word_clean}"
                }
            else:
                return {
                    "matched_tickets": [],
                    "filter_used": f"ticket_id = {word_clean} (not found)"
                }

    # 2. Unassigned tickets
    if "unassigned" in query_lower:
        match = [t for t in tickets if t["assigned_to"] is None]
        return {"matched_tickets": match, "filter_used": "assigned_to = null"}

    # 3. Urgent tickets
    if "urgent" in query_lower:
        match = [t for t in tickets if t["priority"] == "urgent"]
        return {"matched_tickets": match, "filter_used": "priority = urgent"}

    # 4. Open tickets
    if "open" in query_lower:
        match = [t for t in tickets if t["status"] == "open"]
        return {"matched_tickets": match, "filter_used": "status = open"}

    # 5. Tickets by status
    for status in ["in_progress", "resolved"]:
        if status.replace("_", " ") in query_lower or status in query_lower:
            match = [t for t in tickets if t["status"] == status]
            return {"matched_tickets": match, "filter_used": f"status = {status}"}

    # 6. Tickets by priority
    for priority in ["high", "medium", "low"]:
        if priority in query_lower:
            match = [t for t in tickets if t["priority"] == priority]
            return {"matched_tickets": match, "filter_used": f"priority = {priority}"}

    # 7. Tickets by customer name
    for ticket in tickets:
        if ticket["customer_name"].lower() in query_lower:
            match = [t for t in tickets if t["customer_name"] == ticket["customer_name"]]
            return {"matched_tickets": match, "filter_used": f"customer_name = {ticket['customer_name']}"}

    # 8. Assigned to a specific agent
    for ticket in tickets:
        if ticket["assigned_to"] and ticket["assigned_to"].lower() in query_lower:
            agent = ticket["assigned_to"]
            match = [t for t in tickets if t["assigned_to"] == agent]
            return {"matched_tickets": match, "filter_used": f"assigned_to = {agent}"}

    # Fallback — return all tickets
    return {"matched_tickets": tickets, "filter_used": "all tickets"}