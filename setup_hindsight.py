import json, time
import memory

customers = json.load(open("seed_data.json"))

RULES = [  # (name, priority, content). WHY priority: higher-priority rules are injected first
    ("No invented specifics", 100,
     "Never invent ticket numbers, names, times or dates. You may say you are escalating, "
     "but never promise a specific timeframe."),
    ("Never repeat failed steps", 90,
     "Never ask the customer to repeat a step that the history shows already failed."),
    ("Blame the line after a failed replacement", 80,
     "If a replacement device has also failed, conclude the fault is likely on the line, "
     "not the device, and recommend escalation."),
    ("Keep it short", 70, "Keep replies under 90 words and match the customer's technical level."),
]

for c in customers:
    bank = memory.bank_for(c["id"])

    for name, prio, content in RULES:
        try:
            memory._run(lambda cl, n=name, p=prio, t=content: cl.create_directive(
                bank_id=bank, name=n, content=t, priority=p))
        except Exception as e:
            print(f"[directive] {c['id']} / {name}: {e}")

    try:
        memory._run(lambda cl: cl.create_mental_model(
            bank_id=bank,
            name=f"{c['name']} - support profile",
            id=f"profile-{c['id']}",  # WHY custom id: lets the app fetch it by name later
            source_query="Summarize this customer for a support agent: recurring issues, what has been "
                         "tried and failed, what worked, the current state of the problem, "
                         "communication style, and current mood. Be concise.",
            # WHY these limits: every refresh is a paid LLM run on Hindsight's side.
            # delta = only read new memories; the interval = at most one refresh per 15 min.
            trigger={"mode": "delta", "refresh_after_consolidation": True,
                     "min_refresh_interval_seconds": 900},
        ))
    except Exception as e:
        print(f"[mental model] {c['id']}: {e}")

# WHY polling: creating a profile runs in the background, so we wait until it has content
for c in customers:
    for _ in range(24):  # up to about 2 minutes
        mm = memory._run(lambda cl: cl.get_mental_model(
            bank_id=memory.bank_for(c["id"]), mental_model_id=f"profile-{c['id']}"))
        if mm.content:
            print(f"\n--- {c['name']} profile ---\n{mm.content}")
            break
        time.sleep(5)
    else:
        print(f"\n{c['name']}: still empty after waiting, check again in a minute")
