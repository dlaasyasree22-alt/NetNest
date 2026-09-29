import re
import agent

NAME, CID = "Priya Nair", "priya"
MESSAGES = [
    "my wifi is dropping again tonight",
    "it's happening after 7 PM again, same as always",
    "this is the fourth time I'm explaining this",
]

# WHY a fixed rubric with the true history: the judge needs ground truth to know what
# counts as "already tried". Written once, never tweaked to make results look better.
RUBRIC = """You grade one customer support reply.
Ground truth about the customer: WiFi drops every evening after 7 PM. Already tried and FAILED:
restarting/power-cycling the router, changing the WiFi channel, updating firmware to 2.3,
a factory reset, and replacing the router (Hub X2 was replaced by a Hub X3, which also drops).
Answer with exactly two lines:
REPEATS: 1 if the reply asks the customer to DO any already-tried step (only mentioning that it failed does NOT count), else 0
HISTORY: 1 if the reply shows knowledge of her specific past (Hub X3 replacement, earlier failed fixes, prior tickets), else 0"""

def judge(reply: str):
    out = agent._llm([{"role": "system", "content": RUBRIC}, {"role": "user", "content": reply}])
    r = re.search(r"REPEATS:\s*([01])", out)
    h = re.search(r"HISTORY:\s*([01])", out)
    return (int(r.group(1)) if r else 0, int(h.group(1)) if h else 0)

def run(use_memory: bool):
    history, rows = [], []
    for msg in MESSAGES:
        # save=False WHY: evaluation must never write into the real customer memory
        reply, score, facts = agent.respond(CID, NAME, msg, history, use_memory, save=False)
        history += [{"role": "user", "content": msg}, {"role": "assistant", "content": reply}]
        repeats, hist = judge(reply)
        rows.append((repeats, hist, len(facts)))
        # WHY print every reply: so you can eyeball whether the judge got it right
        print(f"\n[memory {'ON' if use_memory else 'OFF'}] {msg}\n  -> {reply}\n  judge: repeats={repeats} history={hist} memories_used={len(facts)}")
    return rows

off, on = run(False), run(True)
def total(rows, i): return sum(r[i] for r in rows)

print("\n| Metric (3 messages) | Memory OFF | Memory ON |")
print("|---|---|---|")
print(f"| Replies asking her to redo a failed step | {total(off,0)} of 3 | {total(on,0)} of 3 |")
print(f"| Replies showing knowledge of her real history | {total(off,1)} of 3 | {total(on,1)} of 3 |")
