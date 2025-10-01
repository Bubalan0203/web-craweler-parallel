import unittest
import os
from unittest.mock import patch
from config import CrawlerConfig, SupabaseConfig, AppConfig, load_config


class TestCrawlerConfig(unittest.TestCase):

    def test_default_values(self):
        config = CrawlerConfig()

        self.assertEqual(config.timeout, 10)
        self.assertEqual(config.max_retries, 2)
        self.assertTrue(config.sequential_enabled)
        self.assertTrue(config.threaded_enabled)
        self.assertTrue(config.async_enabled)
        self.assertEqual(config.threaded_workers, 10)
        self.assertEqual(config.async_concurrent_limit, 50)

    def test_custom_values(self):
        config = CrawlerConfig(
            timeout=20,
            max_retries=5,
            threaded_workers=20,
            async_concurrent_limit=100
        )

        self.assertEqual(config.timeout, 20)
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.threaded_workers, 20)
        self.assertEqual(config.async_concurrent_limit, 100)


class TestSupabaseConfig(unittest.TestCase):

    @patch.dict(os.environ, {
        'VITE_SUPABASE_URL': 'https://test.supabase.co',
        'VITE_SUPABASE_SUPABASE_ANON_KEY': 'test-key-123'
    })
    def test_config_from_env(self):
        config = SupabaseConfig()

        self.assertEqual(config.url, 'https://test.supabase.co')
        self.assertEqual(config.anon_key, 'test-key-123')
        self.assertTrue(config.is_configured)

    def test_config_not_configured(self):
        with patch.dict(os.environ, {}, clear=True):
            config = SupabaseConfig()

            self.assertFalse(config.is_configured)

    def test_custom_values(self):
        config = SupabaseConfig(
            url='https://custom.supabase.co',
            anon_key='custom-key'
        )

        self.assertEqual(config.url, 'https://custom.supabase.co')
        self.assertEqual(config.anon_key, 'custom-key')
        self.assertTrue(config.is_configured)


class TestAppConfig(unittest.TestCase):

    def test_default_values(self):
        config = AppConfig()

        self.assertTrue(config.debug)
        self.assertEqual(config.host, '0.0.0.0')
        self.assertEqual(config.port, 5000)
        self.assertEqual(config.urls_file, 'urls.txt')
        self.assertEqual(config.log_level, 'INFO')
        self.assertIsInstance(config.crawler, CrawlerConfig)
        self.assertIsInstance(config.supabase, SupabaseConfig)

    def test_custom_values(self):
        crawler_config = CrawlerConfig(timeout=15)
        supabase_config = SupabaseConfig(url='https://test.supabase.co', anon_key='key')

        config = AppConfig(
            debug=False,
            host='127.0.0.1',
            port=8000,
            urls_file='custom_urls.txt',
            log_level='DEBUG',
            crawler=crawler_config,
            supabase=supabase_config
        )

        self.assertFalse(config.debug)
        self.assertEqual(config.host, '127.0.0.1')
        self.assertEqual(config.port, 8000)
        self.assertEqual(config.urls_file, 'custom_urls.txt')
        self.assertEqual(config.log_level, 'DEBUG')
        self.assertEqual(config.crawler.timeout, 15)
        self.assertEqual(config.supabase.url, 'https://test.supabase.co')


class TestLoadConfig(unittest.TestCase):

    @patch.dict(os.environ, {
        'DEBUG': 'False',
        'HOST': '127.0.0.1',
        'PORT': '8080',
        'URLS_FILE': 'test_urls.txt',
        'LOG_LEVEL': 'DEBUG'
    })
    def test_load_config_from_env(self):
        config = load_config()

        self.assertFalse(config.debug)
        self.assertEqual(config.host, '127.0.0.1')
        self.assertEqual(config.port, 8080)
        self.assertEqual(config.urls_file, 'test_urls.txt')
        self.assertEqual(config.log_level, 'DEBUG')

    def test_load_config_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            config = load_config()

            self.assertTrue(config.debug)
            self.assertEqual(config.host, '0.0.0.0')
            self.assertEqual(config.port, 5000)
            self.assertEqual(config.urls_file, 'urls.txt')
            self.assertEqual(config.log_level, 'INFO')


if __name__ == '__main__':
    unittest.main()
