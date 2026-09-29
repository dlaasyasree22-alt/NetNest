import memory

for cid in ["priya", "rohan", "ananya"]:
    # WHY type="observation": list_memories can filter by fact type, and observations
    # are Hindsight's consolidated beliefs (as opposed to raw facts)
    obs = memory._run(lambda c, cid=cid: c.list_memories(
        bank_id=memory.bank_for(cid), type="observation", limit=100))
    print(f"{cid}: {obs.total} observations")
    for m in obs.items[:3]:
        print("   -", m.text[:140])

# WHY recall with types: this is the call the agent will use once observations are confirmed
r = memory._run(lambda c: c.recall(
    bank_id=memory.bank_for("priya"),
    query="my wifi is dropping again tonight",
    types=["observation"], budget="mid", max_tokens=1200))
print("recalled observations for Priya:", len(r.results))
