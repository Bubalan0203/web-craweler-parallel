from flask import Flask, render_template
from crawler import crawl_sequential, crawl_parallel

app = Flask(__name__)

# Load URLs from file
with open("urls.txt") as f:
    urls = [line.strip() for line in f.readlines() if line.strip()]

@app.route("/")
def index():
    # Run sequential
    seq_results, seq_time = crawl_sequential(urls)

    # Run parallel
    par_results, par_time = crawl_parallel(urls, workers=10)

    return render_template(
        "index.html",
        seq_results=seq_results,
        par_results=par_results,
        seq_time=seq_time,
        par_time=par_time,
        url_count=len(urls)
    )

if __name__ == "__main__":
    app.run(debug=True)
