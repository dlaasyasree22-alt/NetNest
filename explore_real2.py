import re
import pandas as pd

BRANDS = ["comcastcares", "Ask_Spectrum", "airtel_care"]

df = pd.read_csv("twcs.csv", dtype=str, usecols=[
    "tweet_id", "author_id", "inbound", "created_at", "text", "in_response_to_tweet_id"])

# WHY parse: created_at is text like "Fri Nov 24 ..." which sorts by weekday name, not date
df["when"] = pd.to_datetime(df.created_at, format="%a %b %d %H:%M:%S %z %Y", errors="coerce")

starters = df[(df.inbound == "True") & df.in_response_to_tweet_id.isna()]
replies = (df[(df.inbound == "False") & df.in_response_to_tweet_id.notna()]
           [["in_response_to_tweet_id", "author_id", "text"]]
           .rename(columns={"in_response_to_tweet_id": "tweet_id", "author_id": "brand", "text": "reply"})
           .drop_duplicates("tweet_id"))
answered = starters.merge(replies, on="tweet_id")
answered = answered[answered.brand.isin(BRANDS)].copy()

TOPIC = re.compile(r"internet|wifi|wi-fi|broadband|network|signal|outage|\bdown\b|slow|speed|"
                   r"connection|modem|router|disconnect|drop", re.I)

def clean(t):
    # WHY: removes links and the numeric @ids the dataset left behind, so the text reads like a person wrote it
    return re.sub(r"\s+", " ", re.sub(r"https?://\S+|@\d+", "", t)).strip()

answered["on_topic"] = answered.text.str.contains(TOPIC)
g = (answered.groupby(["author_id", "brand"])
     .agg(tickets=("tweet_id", "size"), on_topic=("on_topic", "sum")).reset_index())
cand = g[g.tickets.between(4, 10) & (g.on_topic >= 3)].sort_values(["on_topic", "tickets"], ascending=False)

print("Customers with 4-10 tickets, 3+ about connectivity, per brand:")
print(cand.groupby("brand").size(), "\n")

for brand in BRANDS:
    for _, c in cand[cand.brand == brand].head(2).iterrows():
        print(f"===== {brand}: {c.tickets} tickets, {c.on_topic} about connectivity =====")
        rows = answered[(answered.author_id == c.author_id) & (answered.brand == brand)].sort_values("when")
        for _, r in rows.iterrows():
            print(f"{r.when:%Y-%m-%d}  {clean(r.text)[:150]}")
        print()

