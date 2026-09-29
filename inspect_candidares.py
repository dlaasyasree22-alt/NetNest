import pandas as pd

df = pd.read_csv('twcs.csv')

# Parse dates correctly
df['dt'] = pd.to_datetime(df['created_at'], format='%a %b %d %H:%M:%S %z %Y')

authors = {
    'Customer A (Angry Repeat)': '294569',
    'Customer B (Technical/Diagnostic)': '141170',
    'Customer C (New/Activation)': '742550'
}

for label, aid in authors.items():
    print(f"\n{'='*25} {label} (Author ID: {aid}) {'='*25}")
    # Get all tweets from this author
    user_tweets = df[df['author_id'] == str(aid)].sort_values('dt')
    
    for _, ut in user_tweets.iterrows():
        print(f"\n[{ut['dt'].strftime('%Y-%m-%d %H:%M')}] CUSTOMER ({ut['tweet_id']}):\n  {ut['text']}")
        
        # Find responses from brand
        # Either in response_tweet_id or tweets where in_response_to_tweet_id == this tweet_id
        brand_replies = df[df['in_response_to_tweet_id'] == ut['tweet_id']].sort_values('dt')
        for _, br in brand_replies.iterrows():
            print(f"  --> [{br['dt'].strftime('%Y-%m-%d %H:%M')}] {br['author_id']}:\n      {br['text']}")
