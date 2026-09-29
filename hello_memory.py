import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

client = Hindsight(
    base_url=os.environ["HINDSIGHT_URL"],
    api_key=os.environ["HINDSIGHT_API_KEY"],
)

BANK = "cust-priya-demo"

client.create_bank(
    bank_id=BANK,
    name="Priya - support history",
    mission="I am a customer support agent. I remember each customer's issues, "
            "their setup, what fixed things, and how frustrated they were.",
)

client.retain(
    bank_id=BANK,
    content="Priya's router keeps dropping WiFi every evening. Firmware update 2.3 fixed it. "
            "She was very frustrated because this was her third ticket.",
    context="support ticket",
    retain_async=False,
)

results = client.recall(
    bank_id=BANK,
    query="What went wrong for Priya before?"
)

for r in results.results:
    print("-", r.text)

print(
    client.reflect(
        bank_id=BANK,
        query="How should I treat Priya on her next ticket?"
    ).text
)

