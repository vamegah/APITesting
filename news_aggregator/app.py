from flask import Flask, render_template, request
import requests
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Function to fetch articles from NewsAPI with pagination and topic filtering
def fetch_articles(page=1, topic="general"):
    """Fetch paginated news articles from News API with error handling."""
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": NEWS_API_KEY,
        "category": topic,
        "pageSize": 4,  # Only 4 articles per page
        "page": page,
        "country": "us"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()

        if data.get("status") != "ok":
            logger.error(f"API returned an error: {data.get('message', 'Unknown error')}")
            return []

        articles = []
        for article in data.get("articles", []):
            if article.get("urlToImage") and article.get("description"):  # Skip incomplete articles
                articles.append({
                    "title": article.get("title", "No Title"),
                    "image": article.get("urlToImage", "static/default.jpg"),
                    "description": article.get("description", "No description available"),
                    "url": article.get("url", "#"),
                    "publishedAt": article.get("publishedAt", "No date available")
                })

        return articles

    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
    except Exception as err:
        logger.error(f"Unexpected error: {err}")

    return []


# Route to display news articles with pagination and filtering
@app.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    topic = request.args.get("topic", None)

    articles = fetch_articles(page, topic)
    return render_template("index.html", articles=articles, page=page, topic=topic)

if __name__ == "__main__":
    app.run(debug=True)
