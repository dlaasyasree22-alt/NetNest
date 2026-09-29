import time
from memory import _run, bank_for

customers = [
    {"id": "cust-bre-v3", "name": "Bre"},
    {"id": "cust-gavin-v3", "name": "Gavin"},
    {"id": "cust-jordan-v3", "name": "Jordan"},
]

# Generalized directives for real ISP support (using same priority structure as v2)
RULES = [
    ("No invented specifics", 100,
     "Never invent ticket numbers, names, times, or dates. Never promise a specific timeframe for resolution or technician arrival."),
    ("Never repeat failed steps", 90,
     "Never ask the customer to repeat a step that the history shows already failed, such as power cycling or checking app status when they already confirmed doing so."),
    ("Respect hardware returns", 80,
     "If the customer explicitly packaged equipment for return after failed setup or verification issues, do not suggest activating it or keeping it. Confirm return process."),
    ("Keep it short", 70,
     "Keep replies under 90 words and match the customer's technical level and tone.")
]

# 1. Install directives on each v3 bank
for c in customers:
    b_id = bank_for(c["id"])
    print(f"\n[*] Configuring directives for bank: {b_id}")
    for n, p, t in RULES:
        try:
            _run(lambda cl, bank=b_id, name=n, content=t, priority=p: cl.create_directive(
                bank_id=bank, name=name, content=content, priority=priority
            ))
            print(f"  [✓] Directive '{n}' added.")
        except Exception as e:
            print(f"  [!] Directive '{n}' note: {e}")

# 2. Create the profile mental models using the EXACT working trigger dictionary
for c in customers:
    b_id = bank_for(c["id"])
    model_id = f"profile-{c['id']}"
    print(f"\n[*] Creating mental model {model_id} in bank {b_id}...")
    
    try:
        _run(lambda cl, bank=b_id, name=c["name"], mid=model_id: cl.create_mental_model(
            bank_id=bank,
            name=f"{name} - support profile",
            id=mid,
            source_query="Summarize this customer for a support agent: recurring issues, hardware/modem details, what has been tried and failed, what worked, current state of the problem, communication style, and mood. Be concise.",
            trigger={
                "mode": "delta",
                "refresh_after_consolidation": True,
                "min_refresh_interval_seconds": 900
            }
        ))
        print(f"[✓] Mental model {model_id} created successfully.")
    except Exception as e:
        print(f"[!] Mental model notice: {e}")

# 3. Poll until Hindsight generates profile content
print("\n[*] Waiting for profiles to generate (polling every 5s)...")
for c in customers:
    b_id = bank_for(c["id"])
    model_id = f"profile-{c['id']}"
    for _ in range(24):  # up to 2 minutes
        try:
            mm = _run(lambda cl, bank=b_id, mid=model_id: cl.get_mental_model(bank_id=bank, mental_model_id=mid))
            content = (mm.content or "").strip()
            if content and "Generating content" not in content:
                print(f"\n--- {c['name']} profile ready ---")
                print(f"{content[:220]}...\n")
                break
        except Exception as e:
            pass
        time.sleep(5)
    else:
        print(f"[!] {model_id} still generating in background.")
