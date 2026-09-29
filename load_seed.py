import json
from datetime import datetime
import memory

data = json.load(open("seed_data.json"))

# WHY an extra ticket: makes Priya's story "even the replacement router failed",
# so a memory-powered agent can infer the fault is on the line, not the device
for c in data:
    if c["id"] == "priya":
        c["tickets"].append({
            "date": "2026-09-28",
            "customer_message": "The new Hub X3 is dropping WiFi every evening after 7 PM too. "
                                "This is the fourth time I'm explaining this. I want it fixed today.",
            "agent_reply": "We're sorry, Priya. We'll escalate this to our network team for a line-side check.",
            "mood": "furious",
            "resolved": False,
        })

for c in data:
    memory.ensure_bank(c["id"], c["name"])
    for t in c["tickets"]:
        outcome = "Outcome: resolved." if t["resolved"] else "Outcome: NOT resolved."
        memory.save_turn(
            c["id"], t["customer_message"], f'{t["agent_reply"]} {outcome}',
            mood=t["mood"],
            timestamp=datetime.strptime(t["date"], "%Y-%m-%d"),
            wait=True,   # WHY: seeding must finish before the demo, speed doesn't matter here
            name=c["name"].split()[0],  # WHY first name: gives Hindsight a real entity to track
        )
    print(f"loaded {c['name']}: {len(c['tickets'])} tickets")

# sanity check: what does the memory now say about Priya's problem?
print(memory.get_context("priya", "what has been tried for the WiFi drops?"))
