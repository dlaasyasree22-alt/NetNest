import os, re
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from groq import Groq
import memory

load_dotenv()
_g = Groq(api_key=os.environ["GROQ_API_KEY"])

# WHY two models: if the first is rate-limited or errors, we silently fall back
MODELS = ["openai/gpt-oss-120b", "qwen/qwen3-32b"]

# WHY a module-level pool: it survives Streamlit reruns, and lets independent calls run at once
_pool = ThreadPoolExecutor(max_workers=4)

def _llm(messages: list[dict]) -> str:
    for model in MODELS:
        for _ in range(2):  # WHY retry twice: free-tier hiccups are usually one-off
            try:
                r = _g.chat.completions.create(model=model, messages=messages)
                text = r.choices[0].message.content or ""
                # WHY strip: qwen sometimes prints its reasoning inside <think> tags
                text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
                if text:
                    return text
            except Exception as e:
                print(f"[llm] {model} failed: {e}")
    return "Sorry, I'm having trouble on my side right now. Could you send that once more?"

def frustration(message: str) -> int:
    # WHY score only the latest message: one cheap call, and it reacts instantly to a bad turn
    out = _llm([
        {"role": "system", "content": "Rate the customer's frustration from 1 (calm) to 5 (furious). Reply with ONLY the digit."},
        {"role": "user", "content": message},
    ])
    m = re.search(r"[1-5]", out)
    return int(m.group()) if m else 3  # WHY default 3: never crash on a weird answer

SYSTEM_WITH_MEMORY = """You are a customer support agent for a home broadband and cable service provider.
You are talking to {name}.

Customer profile (kept up to date by the memory system):
{profile}

Key beliefs from their history:
{observations}

Relevant detail from past tickets:
{raw}

Rules (stored in the memory bank, follow strictly):
{rules}
- Never ask for information you already have above.
- If this is a repeat problem, acknowledge it briefly and skip basic troubleshooting.
- If asked what changed or what happened before, use the dates in the history."""

SYSTEM_NO_MEMORY = """You are a customer support agent for a home broadband and cable service provider.
You have no information about this customer. Give standard troubleshooting help. Keep replies under 90 words."""

def _bullets(items):
    return "\n".join(f"- {i}" for i in items) if items else "- (none)"

def respond(customer_id: str, name: str, message: str, history: list[dict],
            use_memory: bool = True, save: bool = True):
    # WHY start the score now: it doesn't depend on memory, so it runs while memory loads
    score_f = _pool.submit(frustration, message)

    profile, obs, raw, rules = "", [], [], []
    if use_memory:  # fetch: runs whenever memory is ON, including evaluation runs
        prof_f = _pool.submit(memory.get_profile, customer_id)
        ctx_f = _pool.submit(memory.get_context_layers, customer_id, message)
        try:
            rules = memory.get_rules(customer_id)
        except Exception as e:
            print(f"[rules] failed: {e}")
        try:
            profile = prof_f.result()
        except Exception as e:
            print(f"[profile] failed: {e}")  # WHY continue: a missing profile shouldn't kill the chat
        try:
            obs, raw = ctx_f.result()
        except Exception as e:
            print(f"[recall] failed: {e}")

    if profile or obs or raw:
        system = SYSTEM_WITH_MEMORY.format(
            name=name, profile=profile or "(not written yet)",
            observations=_bullets(obs[:8]), raw=_bullets(raw[:6]), rules=_bullets(rules))
    else:
        system = SYSTEM_NO_MEMORY

    # WHY rebuild history: the UI stores extra keys (score, used) that the API would reject
    past = [{"role": m["role"], "content": m["content"]} for m in history[-6:]]
    reply = _llm([{"role": "system", "content": system}] + past + [{"role": "user", "content": message}])
    score = score_f.result()

    if use_memory and save:  # save: WHY the flag, so evaluation runs never pollute real memory
        try:
            memory.save_turn(customer_id, message, reply, mood=f"frustration {score}/5",
                             name=name.split()[0])
        except Exception as e:
            print(f"[save] failed: {e}")

    # WHY one list: the UI shows "Used N memories", counting profile + observations + raw facts
    facts = ([profile] if profile else []) + obs + raw
    return reply, score, facts
