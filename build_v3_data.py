# build_v3_data.py
import re
import html
import json
import pandas as pd

df = pd.read_csv('twcs.csv')
df['dt'] = pd.to_datetime(df['created_at'], format='%a %b %d %H:%M:%S %z %Y')

def clean_text(text: str) -> str:
    """Removes twitter handles, t.co links, extra hashtags, and unescapes entities."""
    # Unescape HTML entities (&amp; -> &, etc.)
    text = html.unescape(text)
    # Strip URL links
    text = re.sub(r'https?://\S+', '', text)
    # Strip @mentions (e.g. @comcastcares, @115900, @294569)
    text = re.sub(r'@\w+', '', text)
    # Clean redundant hashtag symbols but keep the words
    text = re.sub(r'#(\w+)', r'\1', text)
    # Collapse excess whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Define the 3 customers, seed tweet cutoffs, and held-back prompts
customers = {
    "cust-bre-v3": {
        "name": "Bre",
        "author_id": "294569",
        "description": "Chronic intermittent disconnects; false outage reports; cancelled tech confusion",
        # Hold back tweet 2761067 (2017-11-21 04:54)
        "holdout_tweet_id": 2761067,
        "demo_prompt": "It was made a big deal of that I wasn't using the app, yet it doesn't notice when my services are down while the phone line does. What's up with that? And these non-stop outages??"
    },
    "cust-gavin-v3": {
        "name": "Gavin",
        "author_id": "141170",
        "description": "Technical user; Motorola SB6121 modem; upstream bonding failure post-outage",
        # Hold back tweet 170659 (2017-11-24 21:33)
        "holdout_tweet_id": 170659,
        "demo_prompt": "The send icon is blinking blue, the receive icon is green, the link icon is blue, and the online icon is off. My modem is Motorola model sb6121."
    },
    "cust-jordan-v3": {
        "name": "Jordan",
        "author_id": "742550",
        "description": "Tried activating extra room box ($9/mo); failed on SSN mismatch across 2 reps; boxed for return",
        # Hold back final surrender tweet 2629220 (2017-11-17 17:49)
        "holdout_tweet_id": 2629220,
        "demo_prompt": "I just packaged the box up for return. 2 phone sessions, 2 different reps, same SSN roadblock. Can you confirm the return label instructions?"
    }
}

v3_seed = {}

for bank_id, meta in customers.items():
    aid = meta["author_id"]
    holdout_id = meta["holdout_tweet_id"]
    
    # Filter author tweets before or excluding holdout
    u_tweets = df[(df['author_id'] == aid) & (df['tweet_id'] != holdout_id)].sort_values('dt')
    
    turns = []
    for _, ut in u_tweets.iterrows():
        # Get brand responses
        responses = df[df['in_response_to_tweet_id'] == ut['tweet_id']].sort_values('dt')
        
        user_msg = clean_text(ut['text'])
        agent_reply = clean_text(responses.iloc[0]['text']) if not responses.empty else ""
        
        turns.append({
            "timestamp": ut['dt'].isoformat(),
            "customer_message": user_msg,
            "agent_response": agent_reply,
            "tweet_id": int(ut['tweet_id'])
        })
        
    v3_seed[bank_id] = {
        "name": meta["name"],
        "description": meta["description"],
        "demo_prompt": meta["demo_prompt"],
        "turns": turns
    }

with open("seed_data_v3.json", "w") as f:
    json.dump(v3_seed, f, indent=2)

print("Exported seed_data_v3.json successfully!")
for b_id, d in v3_seed.items():
    print(f"\nBank {b_id} ({d['name']}): {len(d['turns'])} historical turns loaded. Holdout prompt ready:")
    print(f"  -> \"{d['demo_prompt']}\"")
