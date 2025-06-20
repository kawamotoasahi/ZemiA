from flask import Flask, render_template, redirect, url_for, flash
import json
from update_log import update_log

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # フラッシュメッセージ用（適宜変更）

@app.route("/")
def index():
    try:
        with open("data/log.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {
            "score": 0,
            "objects": [],
            "image_width": 640,
            "image_height": 480,
            "history": []
        }

    return render_template("index.html",
        score=data["score"],
        objects=data["objects"],
        history=data["history"],
        image_width=data.get("image_width", 640),
        image_height=data.get("image_height", 480)
    )


@app.route("/refresh")
def refresh():
    success, msg = update_log()
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
