# Web Crawler - Parallel Processing Performance Comparison

A high-performance web crawler that demonstrates the power of parallel processing by comparing three different crawling approaches: Sequential, Threaded (ThreadPoolExecutor), and Async (asyncio + aiohttp).

## Features

- **Three Crawling Modes**:
  - Sequential: Traditional synchronous approach
  - Threaded: Multi-threaded parallel processing using ThreadPoolExecutor
  - Async: Asynchronous I/O using asyncio and aiohttp for maximum performance

- **Robust Error Handling**:
  - Automatic retry logic with configurable attempts
  - Detailed error tracking and reporting
  - Timeout management
  - Connection error handling

- **Performance Metrics**:
  - Real-time performance comparison
  - Visual charts and graphs
  - Response time tracking per URL
  - Success/failure rate analysis

- **Data Persistence** (Optional):
  - Supabase integration for historical data tracking
  - Session storage with performance metrics
  - Detailed crawl results per URL

- **Modern Web Interface**:
  - Beautiful, responsive design
  - Interactive charts using Chart.js
  - Tabbed results view
  - Real-time status indicators

## Architecture

```
project/
├── app.py              # Flask application with routes and error handling
├── crawler.py          # Core crawling logic with three approaches
├── config.py           # Configuration management
├── database.py         # Supabase integration for data persistence
├── requirements.txt    # Python dependencies
├── urls.txt           # List of URLs to crawl
├── templates/
│   └── index.html     # Web interface
├── test_crawler.py    # Unit tests for crawler
└── test_config.py     # Unit tests for configuration
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository** (or extract the project files)

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (optional for Supabase):

   Create a `.env` file in the project root or set environment variables:
   ```bash
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

   If you don't configure Supabase, the application will work without data persistence.

5. **Customize URLs** (optional):

   Edit `urls.txt` to add or modify the URLs you want to crawl. Each URL should be on a separate line.

## Usage

### Running the Application

```bash
python app.py
```

The application will start on `http://0.0.0.0:5000` by default.

Open your browser and navigate to `http://localhost:5000` to see the web interface.

### Configuration Options

You can configure the application using environment variables:

- `DEBUG`: Enable/disable debug mode (default: `True`)
- `HOST`: Host to bind to (default: `0.0.0.0`)
- `PORT`: Port to bind to (default: `5000`)
- `URLS_FILE`: Path to URLs file (default: `urls.txt`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

Example:
```bash
export DEBUG=False
export PORT=8080
python app.py
```

### Crawler Configuration

You can modify crawler behavior in `config.py`:

```python
@dataclass
class CrawlerConfig:
    timeout: int = 10                    # Request timeout in seconds
    max_retries: int = 2                 # Number of retry attempts
    sequential_enabled: bool = True      # Enable sequential crawling
    threaded_enabled: bool = True        # Enable threaded crawling
    async_enabled: bool = True           # Enable async crawling
    threaded_workers: int = 10           # Number of threads
    async_concurrent_limit: int = 50     # Concurrent async requests
```

## Running Tests

Run the unit tests to ensure everything is working correctly:

```bash
# Run all tests
python -m unittest discover

# Run specific test file
python -m unittest test_crawler.py

# Run with verbose output
python -m unittest discover -v
```

## Performance Comparison

The application demonstrates significant performance improvements when using parallel approaches:

### Typical Results (220 URLs)

| Approach   | Time (seconds) | Speedup |
|-----------|----------------|---------|
| Sequential | 45.2           | 1.0x    |
| Threaded   | 8.3            | 5.4x    |
| Async      | 6.1            | 7.4x    |

**Note**: Actual performance depends on:
- Network latency
- Server response times
- Number of URLs
- System resources
- Configuration settings

## How It Works

### Sequential Crawling
Processes URLs one at a time, waiting for each request to complete before starting the next:
```python
results = [fetch(url) for url in urls]
```

### Threaded Crawling
Uses ThreadPoolExecutor to process multiple URLs concurrently using threads:
```python
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch, urls))
```

### Async Crawling
Uses asyncio and aiohttp for non-blocking I/O operations, allowing many requests simultaneously:
```python
async with aiohttp.ClientSession() as session:
    tasks = [fetch_async(url, session) for url in urls]
    results = await asyncio.gather(*tasks)
```

## Error Handling

The crawler includes comprehensive error handling:

1. **Timeout Errors**: Automatic retry with configurable attempts
2. **Connection Errors**: Graceful failure with error logging
3. **HTTP Errors**: Status code tracking and error messages
4. **Parsing Errors**: Safe HTML parsing with fallback values
5. **General Exceptions**: Catch-all error handling with detailed logging

## Logging

The application uses Python's logging module with the following format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Configure log level using the `LOG_LEVEL` environment variable:
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about execution (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

## API Endpoints

The application provides several API endpoints:

- `GET /`: Main web interface with crawl results
- `GET /health`: Health check endpoint
- `GET /api/sessions`: Recent crawl sessions (requires Supabase)
- `GET /api/statistics`: Aggregate statistics (requires Supabase)

## Supabase Integration

If configured, the application stores:

1. **Crawl Sessions**: Performance metrics for each run
2. **Crawl Results**: Detailed results for each URL
3. **Statistics**: Aggregate data for analysis

To enable Supabase:
1. Create a Supabase project
2. Run the database migration to create tables
3. Configure environment variables with your credentials

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Ensure all dependencies are installed
   pip install -r requirements.txt
   ```

2. **Connection Errors**:
   - Check your internet connection
   - Verify URLs in `urls.txt` are valid
   - Some servers may block crawler requests

3. **Timeout Issues**:
   - Increase timeout in `config.py`
   - Reduce concurrent requests
   - Check network stability

4. **Memory Issues**:
   - Reduce the number of URLs
   - Lower the concurrent limit for async crawling
   - Reduce threaded workers

## Best Practices

1. **Rate Limiting**: Be respectful of target servers, avoid overwhelming them
2. **User Agent**: The crawler sets a custom User-Agent header
3. **Retries**: Configured automatic retries with backoff
4. **Error Handling**: All errors are caught and logged
5. **Resource Management**: Proper cleanup of connections and resources

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Performance Optimization Tips

1. **Async Mode**: Use async crawling for maximum performance
2. **Concurrent Limit**: Balance between speed and resource usage
3. **Timeout Values**: Lower timeouts for faster failure detection
4. **Connection Pooling**: aiohttp handles connection pooling automatically
5. **DNS Caching**: The async client caches DNS lookups

## Dependencies

- **Flask**: Web framework
- **requests**: HTTP library for synchronous requests
- **aiohttp**: Async HTTP client
- **beautifulsoup4**: HTML parsing
- **supabase**: Database client (optional)
- **lxml**: Fast XML/HTML parser

## License

This project is provided as-is for educational and demonstration purposes.

## Future Enhancements

Potential improvements for future versions:

- [ ] Support for JavaScript-rendered pages (Selenium/Playwright)
- [ ] Content extraction and analysis
- [ ] Link depth/breadth-first crawling
- [ ] Distributed crawling across multiple machines
- [ ] Real-time progress updates via WebSockets
- [ ] Export results to CSV/JSON
- [ ] Advanced filtering and URL patterns
- [ ] Rate limiting per domain
- [ ] Robot.txt compliance checking
- [ ] Sitemap parsing support

## Support

For issues, questions, or suggestions, please open an issue in the project repository.

## Acknowledgments

Built with Python and modern web technologies to demonstrate the power of parallel processing in web crawling applications.
