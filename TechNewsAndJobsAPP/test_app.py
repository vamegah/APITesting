import unittest
import requests_mock
from app import app, fetch_hacker_news

HACKER_NEWS_API_URL = "https://hacker-news.firebaseio.com/v0"

class TestHackerNewsApp(unittest.TestCase):

    def setUp(self):
        """Set up the test client for Flask app."""
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_fetch_hacker_news_news(self):
        """Test fetching latest news stories from Hacker News API."""
        mock_story_ids = [123, 456, 789]
        mock_story_data = {
            123: {"title": "News 1", "url": "https://example.com/news1", "time": 1700000000, "by": "author1", "type": "story"},
            456: {"title": "News 2", "url": "https://example.com/news2", "time": 1700000001, "by": "author2", "type": "story"},
        }

        with requests_mock.Mocker() as mock:
            mock.get(f"{HACKER_NEWS_API_URL}/newstories.json", json=mock_story_ids)
            for story_id, story in mock_story_data.items():
                mock.get(f"{HACKER_NEWS_API_URL}/item/{story_id}.json", json=story)

            news = fetch_hacker_news("newstories", limit=2, offset=0)
            self.assertEqual(len(news), 2)
            self.assertEqual(news[0]["title"], "News 1")
            self.assertEqual(news[1]["title"], "News 2")

    def test_fetch_hacker_news_jobs(self):
        """Test fetching job postings from Hacker News API."""
        mock_job_ids = [101, 102]
        mock_job_data = {
            101: {"title": "Job 1", "url": "https://example.com/job1", "time": 1700000003, "by": "recruiter1", "type": "job"},
            102: {"title": "Job 2", "url": "https://example.com/job2", "time": 1700000004, "by": "recruiter2", "type": "job"},
        }

        with requests_mock.Mocker() as mock:
            mock.get(f"{HACKER_NEWS_API_URL}/jobstories.json", json=mock_job_ids)
            for job_id, job in mock_job_data.items():
                mock.get(f"{HACKER_NEWS_API_URL}/item/{job_id}.json", json=job)

            jobs = fetch_hacker_news("jobstories", limit=1, offset=0)
            self.assertEqual(len(jobs), 1)
            self.assertEqual(jobs[0]["title"], "Job 1")

    def test_index_route_news(self):
        """Test that the index route returns news by default."""
        mock_story_ids = [1001, 1002]
        mock_story_data = {
            1001: {"title": "Tech News 1", "url": "https://example.com/tech1", "time": 1700000010, "by": "dev1", "type": "story"},
            1002: {"title": "Tech News 2", "url": "https://example.com/tech2", "time": 1700000011, "by": "dev2", "type": "story"},
        }

        with requests_mock.Mocker() as mock:
            mock.get(f"{HACKER_NEWS_API_URL}/newstories.json", json=mock_story_ids)
            for story_id, story in mock_story_data.items():
                mock.get(f"{HACKER_NEWS_API_URL}/item/{story_id}.json", json=story)

            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Tech News 1", response.data)
            self.assertIn(b"Tech News 2", response.data)

    def test_index_route_jobs(self):
        """Test that the index route fetches jobs when requested."""
        mock_job_ids = [2001, 2002]
        mock_job_data = {
            2001: {"title": "Developer Job 1", "url": "https://example.com/job1", "time": 1700000020, "by": "hiring1", "type": "job"},
            2002: {"title": "Developer Job 2", "url": "https://example.com/job2", "time": 1700000021, "by": "hiring2", "type": "job"},
        }

        with requests_mock.Mocker() as mock:
            mock.get(f"{HACKER_NEWS_API_URL}/jobstories.json", json=mock_job_ids)
            for job_id, job in mock_job_data.items():
                mock.get(f"{HACKER_NEWS_API_URL}/item/{job_id}.json", json=job)

            response = self.client.get("/?category=jobs")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Developer Job 1", response.data)
            self.assertIn(b"Developer Job 2", response.data)

    def test_pagination(self):
        """Test pagination by limiting results and shifting offset."""
        mock_story_ids = [3001, 3002, 3003, 3004]
        mock_story_data = {
            3001: {"title": "News A", "url": "https://example.com/a", "time": 1700000030, "by": "authorA", "type": "story"},
            3002: {"title": "News B", "url": "https://example.com/b", "time": 1700000031, "by": "authorB", "type": "story"},
            3003: {"title": "News C", "url": "https://example.com/c", "time": 1700000032, "by": "authorC", "type": "story"},
            3004: {"title": "News D", "url": "https://example.com/d", "time": 1700000033, "by": "authorD", "type": "story"},
        }

        with requests_mock.Mocker() as mock:
            mock.get(f"{HACKER_NEWS_API_URL}/newstories.json", json=mock_story_ids)
            for story_id, story in mock_story_data.items():
                mock.get(f"{HACKER_NEWS_API_URL}/item/{story_id}.json", json=story)

            # Fetch first 2 results (offset 0)
            response1 = self.client.get("/?limit=2&offset=0")
            self.assertEqual(response1.status_code, 200)
            self.assertIn(b"News A", response1.data)
            self.assertIn(b"News B", response1.data)
            self.assertNotIn(b"News C", response1.data)

            # Fetch next 2 results (offset 2)
            response2 = self.client.get("/?limit=2&offset=2")
            self.assertEqual(response2.status_code, 200)
            self.assertIn(b"News C", response2.data)
            self.assertIn(b"News D", response2.data)
            self.assertNotIn(b"News A", response2.data)


if __name__ == "__main__":
    unittest.main()
