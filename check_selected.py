import pandas as pd

# Load twcs.csv
df = pd.read_csv('twcs.csv')

# 1. Find the Comcast repeat customer
comcast_repeat = df[df['text'].str.contains('The #XFINITY problems keep going', na=False)]
print("Comcast Repeat Customer:")
print(comcast_repeat[['author_id', 'tweet_id', 'text']])

# 2. Find the Spectrum technical customer
spectrum_tech = df[df['text'].str.contains('Motorola modem model:sb6121', na=False)]
print("\nSpectrum Tech Customer:")
print(spectrum_tech[['author_id', 'tweet_id', 'text']])

# 3. Find 2 Comcast customers with only 2-3 answered tickets for our Short/New profile
comcast_inbound = df[(df['author_id'].str.isnumeric()) & (df['inbound'] == True)]
# Find authors who tweeted to comcastcares
to_comcast = df[df['text'].str.contains('@comcastcares', case=False, na=False)]
author_counts = to_comcast['author_id'].value_counts()
short_candidates = author_counts[(author_counts >= 2) & (author_counts <= 3)].head(5).index.tolist()

print("\nCandidate Short/New Comcast Customers (2-3 tickets):")
for aid in short_candidates:
    sample_text = df[df['author_id'] == aid]['text'].iloc[0]
    print(f"Author {aid}: {sample_text[:100]}...")
