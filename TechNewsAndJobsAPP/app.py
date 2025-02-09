from flask import Flask, render_template, request
import requests

app = Flask(__name__)

HACKER_NEWS_API_URL = "https://hacker-news.firebaseio.com/v0"

def fetch_hacker_news(endpoint, limit=10, offset=0):
    """Fetch top stories or jobs from Hacker News API with pagination."""
    try:
        response = requests.get(f"{HACKER_NEWS_API_URL}/{endpoint}.json")
        response.raise_for_status()
        all_ids = response.json()[offset:offset + limit]  # Pagination
        stories = []

        for story_id in all_ids:
            story = requests.get(f"{HACKER_NEWS_API_URL}/item/{story_id}.json").json()
            if story:
                stories.append({
                    "title": story.get("title", "No title"),
                    "url": story.get("url", "#"),
                    "time": story.get("time", 0),
                    "source": story.get("by", "Unknown"),
                    "type": story.get("type", "story"),
                    "id": story_id
                })

        return stories
    except requests.RequestException:
        return []

@app.route("/")
def index():
    """Display latest news by default."""
    limit = int(request.args.get("limit", 10))
    offset = int(request.args.get("offset", 0))
    category = request.args.get("category", "news")

    if category == "jobs":
        stories = fetch_hacker_news("jobstories", limit, offset)
    else:
        stories = fetch_hacker_news("newstories", limit, offset)

    return render_template("index.html", stories=stories, category=category, limit=limit, offset=offset)

if __name__ == "__main__":
    app.run(debug=True)
