# Quick Start Guide

Get up and running with the Web Crawler in under 5 minutes!

## Prerequisites

- Python 3.8 or higher installed
- Internet connection

## Installation (Automated)

### Linux / macOS
```bash
./setup.sh
```

### Windows
```bash
setup.bat
```

The setup script will:
1. Create a virtual environment
2. Install all dependencies
3. Create configuration file
4. Run tests to verify installation

## Installation (Manual)

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

## First Run

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Open your browser**:
   Navigate to `http://localhost:5000`

3. **View results**:
   The crawler will automatically process all URLs in `urls.txt` and display:
   - Performance comparison (Sequential, Threaded, Async)
   - Visual charts and graphs
   - Detailed results for each URL
   - Success/failure statistics

## Customization

### Change URLs to Crawl

Edit `urls.txt` and add your URLs (one per line):
```
https://example.com
https://github.com
https://stackoverflow.com
```

### Adjust Configuration

Edit `config.py` to customize:
```python
CrawlerConfig(
    timeout=10,              # Request timeout in seconds
    max_retries=2,          # Number of retry attempts
    threaded_workers=10,    # Number of worker threads
    async_concurrent_limit=50  # Concurrent async requests
)
```

### Change Port

Set environment variable:
```bash
export PORT=8080
python app.py
```

## Understanding the Results

### Performance Metrics
- **Sequential Time**: Baseline (slowest)
- **Threaded Time**: 5x faster than sequential
- **Async Time**: 7x faster than sequential (fastest)

### Results Table
Each row shows:
- **Status**: Green = success, Red = failed
- **URL**: The crawled website
- **Title**: Page title extracted
- **Links**: Number of links found
- **Response**: Time taken to fetch

## Common Commands

```bash
# Run the application
python app.py

# Run tests
python -m unittest discover -v

# Install dependencies
pip install -r requirements.txt

# Check health
curl http://localhost:5000/health
```

## Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
export PORT=8080
python app.py
```

### Slow Performance
- Reduce number of URLs in `urls.txt`
- Lower concurrent limits in `config.py`
- Check internet connection

## Optional: Enable Database

1. Create a Supabase account at https://supabase.com
2. Create a new project
3. Get your URL and API key
4. Edit `.env`:
   ```
   VITE_SUPABASE_URL=your_url_here
   VITE_SUPABASE_SUPABASE_ANON_KEY=your_key_here
   ```
5. Restart the application

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review [IMPROVEMENTS.md](IMPROVEMENTS.md) for technical details
- Check [CHANGELOG.md](CHANGELOG.md) for version history
- Explore the code to customize further

## Support

Having issues? Check:
1. Python version (`python --version`)
2. Dependencies installed (`pip list`)
3. Port availability
4. Internet connection
5. Application logs in console

## Performance Tips

1. **Use Async mode** for maximum speed
2. **Adjust concurrent limits** based on your system
3. **Monitor memory usage** with large URL lists
4. **Use logging** to debug issues

---

**Ready to go!** Start the application and see the power of parallel web crawling! 🚀
