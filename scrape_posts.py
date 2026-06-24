"""
Scrape r/MacOS posts and save as JSON.
Requires: pip install praw
"""
import praw
import json
import os
from datetime import datetime

# Get credentials from environment
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = 'takemeter-scraper/1.0'

if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
    print("Error: Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables")
    print("Get these from https://www.reddit.com/prefs/apps")
    exit(1)

# Authenticate with Reddit
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

print("Scraping r/MacOS posts...")
posts = []
seen_ids = set()

# Fetch from multiple sources to get variety
for source in ['hot', 'new', 'top']:
    print(f"  Fetching from '{source}' feed...")
    subreddit = reddit.subreddit('MacOS')

    if source == 'hot':
        posts_iter = subreddit.hot(limit=100)
    elif source == 'new':
        posts_iter = subreddit.new(limit=100)
    else:  # top
        posts_iter = subreddit.top('month', limit=100)

    for post in posts_iter:
        if post.id in seen_ids or len(posts) >= 200:
            continue

        seen_ids.add(post.id)

        # Get post text (title + body if it exists)
        text = post.title
        if post.selftext and len(post.selftext.strip()) > 0:
            text += '\n' + post.selftext[:300]  # Limit body to 300 chars

        posts.append({
            'id': len(posts) + 1,
            'text': text.strip(),
            'reddit_id': post.id,
            'created_utc': post.created_utc,
            'score': post.score
        })

print(f"Scraped {len(posts)} posts")

# Save to JSON
output = [{'id': p['id'], 'text': p['text']} for p in posts]
with open('posts.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Saved {len(output)} posts to posts.json")
print(f"Post count: {len(output)}")
if output:
    print(f"Sample post: {output[0]['text'][:80]}...")
