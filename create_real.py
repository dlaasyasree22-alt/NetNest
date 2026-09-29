import pandas as pd

# WHY dtype=str: the ids are huge numbers with gaps, and reading them as text avoids rounding bugs
df = pd.read_csv("twcs.csv", dtype=str, usecols=[
    "tweet_id", "author_id", "inbound", "created_at", "text", "in_response_to_tweet_id"])

# a "ticket" = a customer message that starts a new thread (not a reply inside one)
starters = df[(df.inbound == "True") & df.in_response_to_tweet_id.isna()]

# WHY only answered tickets: we need the brand's reply, and it tells us WHICH brand was contacted
replies = (df[(df.inbound == "False") & df.in_response_to_tweet_id.notna()]
           [["in_response_to_tweet_id", "author_id"]]
           .rename(columns={"in_response_to_tweet_id": "tweet_id", "author_id": "brand"})
           .drop_duplicates("tweet_id"))
answered = starters.merge(replies, on="tweet_id")

counts = answered.groupby(["author_id", "brand"]).size().reset_index(name="tickets")
repeat = counts[(counts.tickets >= 3) & (counts.tickets <= 12)]  # WHY cap 12: keeps histories a sane size

print("Customers with 3+ answered tickets to the SAME brand, by brand:")
print(repeat.brand.value_counts().head(25))

top = repeat.sort_values("tickets", ascending=False).head(1).iloc[0]
print(f"\nSample: the customer with {top.tickets} tickets to {top.brand}:")
sample = answered[(answered.author_id == top.author_id) & (answered.brand == top.brand)]
for _, r in sample.sort_values("created_at").iterrows():
    print(f"\n{r.created_at}\n  {r.text[:220]}")
