# app.py
import os
import re

from flask import Flask, render_template, request, Blueprint, send_from_directory
from flask_assets import Bundle, Environment

from flask_src.todo import todos

core = Blueprint("core", __name__)

app = Flask(__name__)

assets = Environment(app)
css = Bundle("src/main.css", output="dist/main.css")
js = Bundle("src/*.js", output="dist/main.js")  # new

assets.register("css", css)
assets.register("js", js)  # new
css.build()
js.build()  # new


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/search")
def search_page():
    return render_template("search.html")


@app.route('/images/<path:path>')
def send_report(path: str):
    return send_from_directory('static/images', path)


def rm_path_chars_from_url(s: str) -> str:
    return re.sub('([/\\\\]|\.\.)', '_', s)


@app.route("/videos/<video_name>", methods=["GET"])
def video(video_name: str):
    headers = request.headers
    video_path = os.path.abspath(os.path.join("videos", rm_path_chars_from_url(video_name)))

    if "range" not in headers:
        with open(video_path, "rb") as f:
            size = os.stat(video_path).st_size
            headers = {
                "Content-Range": f"bytes {0}-{size - 1}/{size}",
                "Accept-Ranges": "bytes",
                "Content-Length": size,
                "Content-Type": "video/mp4",
            }
            return app.response_class(f.read(), status=200, headers=headers)

    size = os.stat(video_path)
    size = size.st_size

    chunk_size = (10 ** 6) * 3  # 1000kb makes 1mb * 3 = 3mb (this is based on your choice)
    start = int(re.sub("\D", "", headers["range"]))
    end = min(start + chunk_size, size - 1)

    content_length = end - start + 1

    def get_chunk(video_path, start, chunk_size):
        with open(video_path, "rb") as f:
            f.seek(start)
            chunk = f.read(chunk_size)
        return chunk

    headers = {
        "Content-Range": f"bytes {start}-{end}/{size}",
        "Accept-Ranges": "bytes",
        "Content-Length": content_length,
        "Content-Type": "video/mp4",
    }

    return app.response_class(get_chunk(video_path, start, chunk_size), 206, headers)


@app.route("/search", methods=["POST"])
def search_todo():
    search_term = request.form.get("search")

    if not len(search_term):
        return render_template("todo.html", todos=[])

    res_todos = []
    for todo in todos:
        if search_term in todo["title"]:
            res_todos.append(todo)

    return render_template("todo.html", todos=res_todos)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
