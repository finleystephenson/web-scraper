from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    """Render the home page with URL input form."""
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():
    """Accept URL from form and return placeholder result."""
    url = request.form.get("url", "")
    # Placeholder response - scraping logic comes in Phase 2
    return render_template("index.html", url=url, scanned=True)


if __name__ == "__main__":
    app.run(debug=True)
