import logging
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client
from config import SupabaseConfig

logger = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self, config: SupabaseConfig):
        self.config = config
        self.client: Optional[Client] = None

        if config.is_configured:
            try:
                self.client = create_client(config.url, config.anon_key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
        else:
            logger.warning("Supabase not configured. Database features disabled.")

    def is_available(self) -> bool:
        return self.client is not None

    def save_crawl_session(
        self,
        url_count: int,
        sequential_time: float,
        threaded_time: float,
        async_time: Optional[float] = None,
        success_count: int = 0,
        fail_count: int = 0
    ) -> Optional[str]:
        if not self.is_available():
            logger.warning("Database not available, skipping session save")
            return None

        try:
            data = {
                "url_count": url_count,
                "sequential_time": sequential_time,
                "threaded_time": threaded_time,
                "async_time": async_time,
                "success_count": success_count,
                "fail_count": fail_count,
                "speedup_threaded": round(sequential_time / threaded_time, 2) if threaded_time > 0 else 0,
                "speedup_async": round(sequential_time / async_time, 2) if async_time and async_time > 0 else None,
                "created_at": datetime.utcnow().isoformat()
            }

            result = self.client.table('crawl_sessions').insert(data).execute()
            session_id = result.data[0]['id'] if result.data else None

            logger.info(f"Crawl session saved with ID: {session_id}")
            return session_id

        except Exception as e:
            logger.error(f"Error saving crawl session: {e}")
            return None

    def save_crawl_results(self, session_id: str, results: List[Dict], crawl_type: str) -> bool:
        if not self.is_available() or not session_id:
            return False

        try:
            data = [
                {
                    "session_id": session_id,
                    "crawl_type": crawl_type,
                    "url": result.get("url"),
                    "title": result.get("title"),
                    "links": result.get("links"),
                    "status_code": result.get("status_code"),
                    "error": result.get("error"),
                    "response_time": result.get("response_time"),
                    "success": result.get("success", True)
                }
                for result in results
            ]

            self.client.table('crawl_results').insert(data).execute()
            logger.info(f"Saved {len(results)} crawl results for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving crawl results: {e}")
            return False

    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        if not self.is_available():
            return []

        try:
            result = self.client.table('crawl_sessions')\
                .select('*')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Error fetching recent sessions: {e}")
            return []

    def get_session_results(self, session_id: str) -> List[Dict]:
        if not self.is_available():
            return []

        try:
            result = self.client.table('crawl_results')\
                .select('*')\
                .eq('session_id', session_id)\
                .execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Error fetching session results: {e}")
            return []

    def get_statistics(self) -> Dict:
        if not self.is_available():
            return {}

        try:
            sessions_result = self.client.table('crawl_sessions')\
                .select('*', count='exact')\
                .execute()

            total_sessions = sessions_result.count if hasattr(sessions_result, 'count') else 0

            avg_result = self.client.rpc('get_average_speedup').execute()
            avg_speedup = avg_result.data[0] if avg_result.data else {}

            return {
                "total_sessions": total_sessions,
                "average_speedup_threaded": avg_speedup.get("avg_speedup_threaded", 0),
                "average_speedup_async": avg_speedup.get("avg_speedup_async", 0)
            }

        except Exception as e:
            logger.error(f"Error fetching statistics: {e}")
            return {}
