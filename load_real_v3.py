# load_real_v3.py
import json
import time
from memory import _run

DIRECTIVES = [
    "Never ask a customer to repeat diagnostic steps they already completed (e.g., power cycles, app checks).",
    "Never suggest cancelling a scheduled technician when intermittent disconnects persist.",
    "Do not invent ticket numbers, ETAs, or technician names.",
    "If a customer explicitly chooses to return hardware, provide return instructions without pushing activation or upsells.",
    "Keep responses concise, empathetic, and under 90 words."
]

def load_v3():
    with open("seed_data_v3.json", "r") as f:
        data = json.load(f)

    for bank_id, info in data.items():
        print(f"\n================ Loading {bank_id} ({info['name']}) ================")
        
        # 1. Ensure bank exists
        def init_bank(client):
            client.create_bank(
                bank_id=bank_id,
                name=f"Customer Support - {info['name']}",
                mission="Provide context-aware broadband and hardware support without repeating failed troubleshooting."
            )
        try:
            _run(init_bank)
            print(f"[✓] Created bank {bank_id}")
        except Exception as e:
            print(f"[i] Bank {bank_id} notice: {e}")

        # 2. Add generalized directives
        def set_directives(client):
            for d in DIRECTIVES:
                client.create_directive(bank_id=bank_id, content=d)
        try:
            _run(set_directives)
            print(f"[✓] Added {len(DIRECTIVES)} directives")
        except Exception as e:
            print(f"[!] Directive creation note: {e}")

        # 3. Retain historical turns with real timestamps
        print(f"[*] Ingesting {len(info['turns'])} turns (synchronous)...")
        for idx, turn in enumerate(info['turns'], start=1):
            ts = turn["timestamp"]
            text_block = f"Customer: {turn['customer_message']}\nSupport: {turn['agent_response']}"
            
            def retain_turn(client, tb=text_block, tstamp=ts):
                client.retain(
                    bank_id=bank_id,
                    content=tb,
                    timestamp=tstamp,
                    retain_async=False
                )
            
            _run(retain_turn)
            print(f"    - Turn {idx}/{len(info['turns'])} ({ts[:10]}) retained.")

        # 4. Create mental model (profile-<id>)
        # Profile summarizes customer temperament, hardware setup, and chronic issues
        model_id = f"profile-{bank_id}"
        def create_mental_model(client):
            client.create_mental_model(
                bank_id=bank_id,
                model_id=model_id,
                name=f"Profile for {info['name']}",
                description="Living summary of customer technical setup, reported issues, and service status.",
                refresh_interval=900,
                refresh_on_consolidation=True
            )
        try:
            _run(create_mental_model)
            print(f"[✓] Initiated mental model: {model_id}")
        except Exception as e:
            print(f"[!] Mental model notice: {e}")

    print("\nAll v3 banks seeded successfully!")

if __name__ == "__main__":
    load_v3()
