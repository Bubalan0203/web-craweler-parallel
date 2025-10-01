from flask import Flask, render_template, jsonify, request
import logging
from pathlib import Path
from typing import List

from config import load_config
from crawler import crawl_sequential, crawl_parallel, crawl_async_wrapper
from database import DatabaseService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
config = load_config()
db_service = DatabaseService(config.supabase)


def load_urls(file_path: str) -> List[str]:
    try:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"URLs file not found: {file_path}")
            return []

        with open(file_path) as f:
            urls = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

        logger.info(f"Loaded {len(urls)} URLs from {file_path}")
        return urls

    except Exception as e:
        logger.error(f"Error loading URLs: {e}")
        return []


@app.route("/")
def index():
    try:
        urls = load_urls(config.urls_file)

        if not urls:
            return render_template(
                "index.html",
                error="No URLs found. Please check urls.txt file.",
                url_count=0
            )

        logger.info(f"Starting crawl for {len(urls)} URLs")

        seq_results, seq_time = crawl_sequential(urls)
        logger.info(f"Sequential crawl completed in {seq_time}s")

        par_results, par_time = crawl_parallel(urls, workers=config.crawler.threaded_workers)
        logger.info(f"Parallel (threaded) crawl completed in {par_time}s")

        async_results, async_time = None, None
        if config.crawler.async_enabled:
            try:
                async_results, async_time = crawl_async_wrapper(
                    urls,
                    concurrent_limit=config.crawler.async_concurrent_limit
                )
                logger.info(f"Async crawl completed in {async_time}s")
            except Exception as e:
                logger.error(f"Error in async crawl: {e}")

        success_count = sum(1 for r in par_results if r.get('success', False))
        fail_count = len(par_results) - success_count

        if db_service.is_available():
            session_id = db_service.save_crawl_session(
                url_count=len(urls),
                sequential_time=seq_time,
                threaded_time=par_time,
                async_time=async_time,
                success_count=success_count,
                fail_count=fail_count
            )

            if session_id:
                db_service.save_crawl_results(session_id, seq_results, 'sequential')
                db_service.save_crawl_results(session_id, par_results, 'threaded')
                if async_results:
                    db_service.save_crawl_results(session_id, async_results, 'async')

        return render_template(
            "index.html",
            seq_results=seq_results,
            par_results=par_results,
            async_results=async_results,
            seq_time=seq_time,
            par_time=par_time,
            async_time=async_time,
            url_count=len(urls),
            success_count=success_count,
            fail_count=fail_count,
            db_enabled=db_service.is_available()
        )

    except Exception as e:
        logger.error(f"Error in index route: {e}", exc_info=True)
        return render_template(
            "index.html",
            error=f"An error occurred: {str(e)}",
            url_count=0
        )


@app.route("/api/sessions")
def get_sessions():
    try:
        sessions = db_service.get_recent_sessions(limit=20)
        return jsonify({"success": True, "sessions": sessions})
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/statistics")
def get_statistics():
    try:
        stats = db_service.get_statistics()
        return jsonify({"success": True, "statistics": stats})
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "database": db_service.is_available()
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    logger.info(f"Starting application on {config.host}:{config.port}")
    app.run(
        debug=config.debug,
        host=config.host,
        port=config.port
    )
