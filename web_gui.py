from flask import Flask, request, render_template
from web_search import retrieval

app = Flask(__name__)

@app.route("/")
def index():
    user_query = request.args.get("user_query", "")
    results, timed = retrieval(user_query)
    return render_template('index.html',  results = results, timed = str(timed))
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)