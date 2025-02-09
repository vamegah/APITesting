import unittest
from unittest.mock import patch, Mock
from app import fetch_articles

class TestFetchArticles(unittest.TestCase):

    @patch("requests.get")
    def test_fetch_articles_success(self, mock_get):
        """Test fetch_articles with a valid API response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "Test Article",
                    "urlToImage": "https://example.com/image.jpg",
                    "description": "This is a test description.",
                    "url": "https://example.com",
                    "publishedAt": "2025-02-07T12:00:00Z"
                }
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        articles = fetch_articles(page=1, topic="technology")
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "Test Article")

    @patch("requests.get")
    def test_fetch_articles_empty_list(self, mock_get):
        """Test fetch_articles when API returns no articles."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok", "articles": []}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        articles = fetch_articles(page=1, topic="technology")
        self.assertEqual(len(articles), 0)

    @patch("requests.get")
    def test_fetch_articles_missing_fields(self, mock_get):
        """Test fetch_articles skips articles with missing image or description."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {"title": "No Image", "urlToImage": None, "description": "Valid description.", "url": "https://example.com", "publishedAt": "2025-02-07T12:00:00Z"},
                {"title": "No Description", "urlToImage": "https://example.com/image.jpg", "description": None, "url": "https://example.com", "publishedAt": "2025-02-07T12:00:00Z"},
                {"title": "Valid Article", "urlToImage": "https://example.com/image.jpg", "description": "Valid content.", "url": "https://example.com", "publishedAt": "2025-02-07T12:00:00Z"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        articles = fetch_articles(page=1, topic="technology")
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "Valid Article")

    @patch("requests.get")
    def test_fetch_articles_invalid_topic(self, mock_get):
        """Test fetch_articles when an invalid topic is provided."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "error", "message": "Invalid category"}
        mock_response.status_code = 400
        mock_get.return_value = mock_response

        articles = fetch_articles(page=1, topic="invalid_topic")
        self.assertEqual(len(articles), 0)

    @patch("requests.get")
    def test_fetch_articles_api_failure(self, mock_get):
        """Test fetch_articles handles API failures gracefully."""
        mock_get.side_effect = Exception("API call failed")

        articles = fetch_articles(page=1, topic="technology")
        self.assertEqual(len(articles), 0)

    @patch("requests.get")
    def test_pagination_first_page(self, mock_get):
            """Test fetch_articles returns correct number of articles for page 1."""
            mock_response = Mock()
            mock_response.json.return_value = {
                "status": "ok",
                "articles": [
                    {"title": f"Article {i}", "urlToImage": f"https://example.com/image{i}.jpg", 
                    "description": f"Description {i}", "url": f"https://example.com/{i}", 
                    "publishedAt": "2025-02-07T12:00:00Z"}
                    for i in range(4)  # Page should return exactly 4 articles
                ]
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            articles = fetch_articles(page=1, topic="technology")
            self.assertEqual(len(articles), 4)
            self.assertEqual(articles[0]["title"], "Article 0")
            self.assertEqual(articles[3]["title"], "Article 3")

    @patch("requests.get")
    def test_pagination_next_page(self, mock_get):
        """Test fetch_articles returns correct articles for page 2."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {"title": f"Article {i+4}", "urlToImage": f"https://example.com/image{i+4}.jpg",
                 "description": f"Description {i+4}", "url": f"https://example.com/{i+4}",
                 "publishedAt": "2025-02-07T12:00:00Z"}
                for i in range(4)  # Page 2 should return the next 4 articles
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        articles = fetch_articles(page=2, topic="technology")
        self.assertEqual(len(articles), 4)
        self.assertEqual(articles[0]["title"], "Article 4")
        self.assertEqual(articles[3]["title"], "Article 7")

    @patch("requests.get")
    def test_pagination_empty_page(self, mock_get):
        """Test fetch_articles returns an empty list when no articles are available on a page."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok", "articles": []}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        articles = fetch_articles(page=10, topic="technology")  # Assume page 10 has no data
        self.assertEqual(len(articles), 0)

if __name__ == "__main__":
    unittest.main()
