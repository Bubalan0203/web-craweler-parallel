import unittest
from unittest.mock import Mock, patch, MagicMock
import time
from crawler import WebCrawler, CrawlResult, crawl_sequential, crawl_parallel


class TestCrawlResult(unittest.TestCase):

    def test_crawl_result_success(self):
        result = CrawlResult(
            url="https://example.com",
            title="Example Domain",
            links=5,
            status_code=200,
            response_time=0.5,
            success=True
        )

        self.assertEqual(result.url, "https://example.com")
        self.assertEqual(result.title, "Example Domain")
        self.assertEqual(result.links, 5)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.success)
        self.assertIsNone(result.error)

    def test_crawl_result_failure(self):
        result = CrawlResult(
            url="https://invalid.com",
            title="Error",
            links=0,
            error="Connection timeout",
            response_time=10.0,
            success=False
        )

        self.assertEqual(result.url, "https://invalid.com")
        self.assertEqual(result.title, "Error")
        self.assertEqual(result.links, 0)
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Connection timeout")


class TestWebCrawler(unittest.TestCase):

    def setUp(self):
        self.crawler = WebCrawler(timeout=5, max_retries=1)

    @patch('crawler.requests.get')
    def test_fetch_sync_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><head><title>Test Page</title></head><body><a href="/link1">Link</a></body></html>'
        mock_get.return_value = mock_response

        result = self.crawler.fetch_sync("https://example.com")

        self.assertTrue(result.success)
        self.assertEqual(result.title, "Test Page")
        self.assertEqual(result.links, 1)
        self.assertEqual(result.status_code, 200)
        self.assertIsNone(result.error)

    @patch('crawler.requests.get')
    def test_fetch_sync_timeout(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        result = self.crawler.fetch_sync("https://timeout.com")

        self.assertFalse(result.success)
        self.assertEqual(result.title, "Timeout Error")
        self.assertEqual(result.links, 0)
        self.assertEqual(result.error, "Request timed out")

    @patch('crawler.requests.get')
    def test_fetch_sync_connection_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        result = self.crawler.fetch_sync("https://unreachable.com")

        self.assertFalse(result.success)
        self.assertEqual(result.title, "Connection Error")
        self.assertEqual(result.links, 0)
        self.assertIn("Connection failed", result.error)

    @patch('crawler.requests.get')
    def test_fetch_sync_no_title(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>No title here</body></html>'
        mock_get.return_value = mock_response

        result = self.crawler.fetch_sync("https://example.com")

        self.assertTrue(result.success)
        self.assertEqual(result.title, "No Title")

    def test_crawl_sequential(self):
        urls = [
            "https://example.com",
            "https://example.org",
            "https://example.net"
        ]

        with patch.object(self.crawler, 'fetch_sync') as mock_fetch:
            mock_fetch.return_value = CrawlResult(
                url="https://example.com",
                title="Test",
                links=5,
                success=True
            )

            results, elapsed_time = self.crawler.crawl_sequential(urls)

            self.assertEqual(len(results), 3)
            self.assertIsInstance(elapsed_time, float)
            self.assertGreaterEqual(elapsed_time, 0)
            self.assertEqual(mock_fetch.call_count, 3)

    def test_crawl_threaded(self):
        urls = [
            "https://example.com",
            "https://example.org",
            "https://example.net"
        ]

        with patch.object(self.crawler, 'fetch_sync') as mock_fetch:
            mock_fetch.return_value = CrawlResult(
                url="https://example.com",
                title="Test",
                links=5,
                success=True
            )

            results, elapsed_time = self.crawler.crawl_threaded(urls, workers=2)

            self.assertEqual(len(results), 3)
            self.assertIsInstance(elapsed_time, float)
            self.assertGreaterEqual(elapsed_time, 0)
            self.assertEqual(mock_fetch.call_count, 3)


class TestCrawlerFunctions(unittest.TestCase):

    @patch('crawler.WebCrawler.crawl_sequential')
    def test_crawl_sequential_wrapper(self, mock_crawl):
        mock_crawl.return_value = ([{"url": "test"}], 1.5)

        urls = ["https://example.com"]
        results, time_taken = crawl_sequential(urls)

        self.assertEqual(len(results), 1)
        self.assertEqual(time_taken, 1.5)
        mock_crawl.assert_called_once_with(urls)

    @patch('crawler.WebCrawler.crawl_threaded')
    def test_crawl_parallel_wrapper(self, mock_crawl):
        mock_crawl.return_value = ([{"url": "test"}], 0.8)

        urls = ["https://example.com"]
        results, time_taken = crawl_parallel(urls, workers=5)

        self.assertEqual(len(results), 1)
        self.assertEqual(time_taken, 0.8)
        mock_crawl.assert_called_once_with(urls, 5)


class TestWebCrawlerRetries(unittest.TestCase):

    def setUp(self):
        self.crawler = WebCrawler(timeout=5, max_retries=3)

    @patch('crawler.requests.get')
    def test_retry_logic_eventual_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><head><title>Success</title></head></html>'

        import requests
        mock_get.side_effect = [
            requests.exceptions.Timeout(),
            requests.exceptions.Timeout(),
            mock_response
        ]

        result = self.crawler.fetch_sync("https://example.com")

        self.assertTrue(result.success)
        self.assertEqual(result.title, "Success")
        self.assertEqual(mock_get.call_count, 3)

    @patch('crawler.requests.get')
    def test_retry_logic_all_failures(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()

        result = self.crawler.fetch_sync("https://example.com")

        self.assertFalse(result.success)
        self.assertEqual(result.error, "Request timed out")
        self.assertEqual(mock_get.call_count, 3)


if __name__ == '__main__':
    unittest.main()
