import memory

# WHY two queries: one is the exact message the eval used, one is the query that worked when we loaded the data
for q in ["my wifi is dropping again tonight", "what has been tried for the WiFi drops?"]:
    try:
        r = memory.get_context("priya", q)
        print(f"{len(r)} memories for: {q}")
    except Exception as e:
        print(f"ERROR for: {q} -> {e}")

# WHY: confirms the bank still holds her history
print("total stored:", memory.list_memories("priya", limit=5).total)
