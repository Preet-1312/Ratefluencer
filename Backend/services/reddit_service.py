import praw
import os

def get_reddit_trends():
    # reddit = praw.Reddit(
    #     client_id=os.getenv("REDDIT_CLIENT_ID"),
    #     client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    #     user_agent=os.getenv("REDDIT_USER_AGENT")
    # )
    # subreddits = [
    #     "artificial", "technology", "startups",
    #     "finance", "MachineLearning", "business"
    # ]
    # trends = []
    # for sub in subreddits:
    #     for post in reddit.subreddit(sub).hot(limit=5):
    #         trends.append({
    #             "source": f"reddit/r/{sub}",
    #             "title": post.title,
    #             "score": post.score,
    #             "comments": post.num_comments,
    #             "url": f"https://reddit.com{post.permalink}"
    #         })
    # return trends
    return []