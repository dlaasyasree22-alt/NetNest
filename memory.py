import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

def _run(fn):
    # WHY a fresh thread + fresh client per call: Streamlit's own thread confuses the
    # client's async internals ("Timeout context manager should be used inside a task").
    # A plain worker thread has a clean slate, same as running from the terminal.
    def work():
        # WHY "with": closes the connection when done, so no unclosed-session leaks
        with Hindsight(
            base_url=os.environ["HINDSIGHT_URL"],
            api_key=os.environ["HINDSIGHT_API_KEY"],
            timeout=60.0,  # WHY 60: cold starts can be slow, and the default would fail mid-demo
        ) as client:
            return fn(client)
    with ThreadPoolExecutor(max_workers=1) as ex:
        return ex.submit(work).result()

def bank_for(customer_id: str) -> str:
    # Pass through directly if it's already a full bank ID (like "cust-bre-v3")
    if customer_id.startswith("cust-") and ("-v2" in customer_id or "-v3" in customer_id):
        return customer_id
    # Default to v3 for short names ("bre" -> "cust-bre-v3"), while letting explicit v2 calls work
    return f"cust-{customer_id}-v3"

def ensure_bank(customer_id: str, name: str) -> None:
    try:
        _run(lambda c: c.create_bank(
            bank_id=bank_for(customer_id),
            name=name,
            mission="I am a customer support agent. I remember each customer's issues, "
                    "their setup, what fixed things, what failed, and how frustrated they were.",
        ))
    except Exception as e:
        # WHY not crash: the bank may already exist, which is fine on re-runs
        print(f"[ensure_bank] {customer_id}: {e}")

def get_context(customer_id: str, message: str) -> list[str]:
    # WHY budget="mid": "high" is slower, and a chat needs to feel instant
    results = _run(lambda c: c.recall(
        bank_id=bank_for(customer_id),
        query=message,
        budget="mid",
        max_tokens=1500,  # WHY cap: keeps the LLM prompt small and inside free-tier limits
    ))
    return [r.text for r in results.results]

def save_turn(customer_id: str, customer_msg: str, agent_reply: str,
              mood: str = "", timestamp: datetime | None = None,
              wait: bool = False, name: str = "Customer") -> None:
    # WHY the real name: Hindsight extracts "who" from the text, so a name
    # gives it a proper entity to attach memories to
    content = f"{name} said: {customer_msg}\nSupport agent replied: {agent_reply}"
    if mood:
        content += f"\n{name}'s mood: {mood}"
    _run(lambda c: c.retain(
        bank_id=bank_for(customer_id),
        content=content,
        context="support conversation",
        timestamp=timestamp,
        retain_async=not wait,  # WHY async in live chat: no lag; seeding uses wait=True
    ))

def list_memories(customer_id: str, limit: int = 50):
    return _run(lambda c: c.list_memories(bank_id=bank_for(customer_id), limit=limit))

def reflect(customer_id: str, query: str) -> str:
    # WHY budget="low": the handoff brief should appear fast, and it's a short summary
    return _run(lambda c: c.reflect(bank_id=bank_for(customer_id), query=query, budget="low")).text
def get_profile(customer_id: str) -> str:
    # The mental model Hindsight keeps up to date for this customer
    try:
        mm = _run(lambda c: c.get_mental_model(
            bank_id=bank_for(customer_id), mental_model_id=f"profile-{customer_id}"))
    except Exception as e:
        print(f"[profile] {customer_id}: {e}")
        return ""
    text = (mm.content or "").strip()
    # WHY: while Hindsight is still writing, the content is a "Generating..." placeholder,
    # and showing that to a customer-facing agent would be worse than showing nothing
    return "" if text.lower().startswith("generating") else text

def list_observations(customer_id: str, limit: int = 8) -> list[str]:
    # Consolidated beliefs, newest first. WHY type="observation": raw facts repeat themselves,
    # observations are Hindsight's deduplicated version
    res = _run(lambda c: c.list_memories(
        bank_id=bank_for(customer_id), type="observation", limit=100))
    items = sorted(res.items, key=lambda m: m.updated_at or "", reverse=True)
    return [m.text.split(" | ")[0] for m in items[:limit]]  # split hides the date/entity suffix

def get_context_layers(customer_id: str, message: str):
    # Two recalls in ONE client session: observations first (clean beliefs), then a few raw
    # facts for detail. WHY: shorter, less repetitive prompt than 20 loose facts
    def work(c):
        bank = bank_for(customer_id)
        obs = c.recall(bank_id=bank, query=message, types=["observation"],
                       budget="mid", max_tokens=800)
        raw = c.recall(bank_id=bank, query=message, types=["world", "experience"],
                       budget="mid", max_tokens=600)
        return obs, raw
    obs, raw = _run(work)
    return [r.text for r in obs.results], [r.text for r in raw.results][:6]

_DEFAULT_RULES = [
    "Never invent ticket numbers, names, times or dates. You may say you are escalating, but never promise a timeframe.",
    "Never ask the customer to repeat a step that the history shows already failed.",
    "If a replacement device has also failed, conclude the fault is likely on the line and recommend escalation.",
    "Keep replies under 90 words and match the customer's technical level.",
]
_rules_cache: dict = {}

def get_rules(customer_id: str) -> list[str]:
    # The directives we stored in Hindsight, read back so the bank is the single source of truth
    if customer_id in _rules_cache:
        return _rules_cache[customer_id]
    rules = []
    try:
        res = _run(lambda c: c.list_directives(bank_id=bank_for(customer_id)))
        items = getattr(res, "items", res)  # WHY defensive: I haven't seen this response's exact shape
        items = sorted(items, key=lambda d: getattr(d, "priority", 0) or 0, reverse=True)
        rules = [d.content for d in items if getattr(d, "is_active", True)]
    except Exception as e:
        print(f"[rules] {customer_id}: {e}")
    rules = rules or _DEFAULT_RULES  # WHY fallback: the demo must never lose its rules to an API hiccup
    _rules_cache[customer_id] = rules
    return rules
