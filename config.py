import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class CrawlerConfig:
    timeout: int = 10
    max_retries: int = 2
    sequential_enabled: bool = True
    threaded_enabled: bool = True
    async_enabled: bool = True
    threaded_workers: int = 10
    async_concurrent_limit: int = 50


@dataclass
class SupabaseConfig:
    url: Optional[str] = None
    anon_key: Optional[str] = None

    def __post_init__(self):
        if not self.url:
            self.url = os.getenv('VITE_SUPABASE_URL')
        if not self.anon_key:
            self.anon_key = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')

    @property
    def is_configured(self) -> bool:
        return bool(self.url and self.anon_key)


@dataclass
class AppConfig:
    debug: bool = True
    host: str = '0.0.0.0'
    port: int = 5000
    urls_file: str = 'urls.txt'
    log_level: str = 'INFO'

    crawler: CrawlerConfig = None
    supabase: SupabaseConfig = None

    def __post_init__(self):
        if self.crawler is None:
            self.crawler = CrawlerConfig()
        if self.supabase is None:
            self.supabase = SupabaseConfig()


def load_config() -> AppConfig:
    return AppConfig(
        debug=os.getenv('DEBUG', 'True').lower() == 'true',
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        urls_file=os.getenv('URLS_FILE', 'urls.txt'),
        log_level=os.getenv('LOG_LEVEL', 'INFO')
    )
