from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DOWNLOAD_FOLDER = "downloads"
app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    try:
        url = request.form.get("url")
        quality = request.form.get("quality")
        f_type = request.form.get("type")

        if not url:
            flash("Invalid or empty URL", "danger")
            return redirect(url_for("home"))

        ydl_opts = {
            "outtmpl": os.path.join(app.config["DOWNLOAD_FOLDER"], "%(title)s.%(ext)s"),
            "quiet": True,
        }

        # VIDEO
        if f_type == "video":
            if quality:
                ydl_opts["format"] = f"bestvideo[height<={quality[:-1]}]+bestaudio/best"
            else:
                ydl_opts["format"] = "best"

        # AUDIO
        else:
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            # If audio converted to mp3
            if f_type != "video":
                filename = os.path.splitext(filename)[0] + ".mp3"

        return send_from_directory(
            app.config["DOWNLOAD_FOLDER"],
            os.path.basename(filename),
            as_attachment=True
        )

    except Exception as e:
        flash(f"Something went wrong: {str(e)}", "danger")
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
