from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    send_from_directory,
)
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
VIDEO_FOLDER = "videos"
THUMBNAIL_FOLDER = "thumbnails"
ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm"}
app.config["VIDEO_FOLDER"] = VIDEO_FOLDER
app.config["THUMBNAIL_FOLDER"] = THUMBNAIL_FOLDER

# Ensure folders exist
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)


def is_allowed_file(filename) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def create_thumbnail(video_path, thumbnail_path):
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                video_path,
                "-ss",
                "00:00:01.000",
                "-vframes",
                "1",
                thumbnail_path,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error generating thumbnail: {e}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part"

    file = request.files["file"]
    if file.filename == "":
        return "No file selected"

    if not is_allowed_file(file.filename):
        return "Invalid file type"

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["VIDEO_FOLDER"], filename)
    file.save(filepath)

    thumbnail_filename = f"{os.path.splitext(filename)[0]}.jpg"
    thumbnail_path = os.path.join(app.config["THUMBNAIL_FOLDER"], thumbnail_filename)
    create_thumbnail(filepath, thumbnail_path)
    return redirect("/")


@app.route("/videos")
def list_videos():
    video_files = [
        f for f in os.listdir(app.config["VIDEO_FOLDER"]) if is_allowed_file(f)
    ]

    video_with_thumbnails = [
        {"filename": video, "thumbnail": f"{os.path.splitext(video)[0]}.jpg"}
        for video in video_files
    ]
    return render_template("video_list.html", videos=video_with_thumbnails)


@app.route("/videos/<filename>")
def stream_video(filename):
    file_extension = filename.rsplit(".", 1)[1].lower()
    mime_type = f"video/{'mp4' if file_extension == 'mp4' else 'x-matroska' if file_extension == 'mkv' else file_extension}"
    return render_template("stream_video.html", filename=filename, mime_type=mime_type)


@app.route("/videos/files/<filename>")
def video_file(filename):
    return send_from_directory(app.config["VIDEO_FOLDER"], filename)


@app.route("/thumbnails/<filename>")
def thumbnail_file(filename):
    return send_from_directory(app.config["THUMBNAIL_FOLDER"], filename)

@app.route("/videos/download/<filename>")
def download_video(filename):
    return send_from_directory(app.config["VIDEO_FOLDER"], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
