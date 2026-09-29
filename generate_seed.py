import json, os, time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
g = Groq(api_key=os.environ["GROQ_API_KEY"])

COMPANY = "NetNest, a home broadband and WiFi router provider in India"

# WHY fixed briefs: we control the STORY (repeat issue, tone, history depth)
# and let the LLM fill in realistic details (router models, error codes, wording)
CUSTOMERS = [
    {"id": "priya", "name": "Priya Nair", "tickets": 6,
     "brief": "Angry repeat-issue customer. Same problem keeps coming back: WiFi drops every "
              "evening on her NetNest Hub X2 router. Restart failed, changing the WiFi channel failed, "
              "firmware 2.3 fixed it for two weeks, then it returned. Each ticket she is more "
              "frustrated and says she is tired of repeating herself. Last ticket is fairly recent."},
    {"id": "rohan", "name": "Rohan Mehta", "tickets": 4,
     "brief": "Calm, technical customer (a software engineer). Wants short, precise answers, "
              "hates generic troubleshooting scripts. Issues: high latency to gaming servers, "
              "a port forwarding problem, and a DNS setting he already fixed himself."},
    {"id": "ananya", "name": "Ananya Iyer", "tickets": 1,
     "brief": "New customer with a single ticket about setting up her first router. Friendly, "
              "not technical, slightly confused by the app."},
]

PROMPT = """Generate realistic customer support history for {company}.
Customer: {name}
Story: {brief}

Return ONLY valid JSON, no markdown, in this exact shape:
{{"tickets": [{{"date": "YYYY-MM-DD", "customer_message": "...", "agent_reply": "...", "mood": "...", "resolved": true}}]}}

Rules:
- Exactly {n} tickets, oldest first, dates between 2026-07-28 and 2026-09-22, spread out over time.
- Use realistic details: router model names, firmware versions, error messages, ISP wording.
- customer_message is 1-3 sentences in the customer's real voice. agent_reply is 1-3 sentences.
- mood is one or two words (e.g. "annoyed", "furious", "calm").
"""

def generate(c):
    for attempt in range(3):  # WHY retry: LLMs sometimes return broken JSON
        try:
            r = g.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": PROMPT.format(
                    company=COMPANY, name=c["name"], brief=c["brief"], n=c["tickets"])}],
            )
            text = r.choices[0].message.content.strip()
            text = text.replace("```json", "").replace("```", "").strip()  # WHY: strip fences if the model adds them
            return json.loads(text)["tickets"]
        except Exception as e:
            print(f"  retry {attempt + 1} for {c['name']}: {e}")
            time.sleep(3)
    raise RuntimeError(f"Could not generate data for {c['name']}")

out = []
for c in CUSTOMERS:
    print(f"Generating {c['name']}...")
    out.append({"id": c["id"], "name": c["name"], "tickets": generate(c)})

json.dump(out, open("seed_data.json", "w"), indent=2)

# preview the hero customer so we can sanity-check before loading anything into memory
for t in out[0]["tickets"]:
    print(f"\n{t['date']} [{t['mood']}] resolved={t['resolved']}")
    print("  C:", t["customer_message"])
    print("  A:", t["agent_reply"])
