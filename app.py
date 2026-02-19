from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from pytubefix import YouTube
from werkzeug.utils import secure_filename
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

        yt = YouTube(url)
        safe_title = secure_filename(yt.title)

        # VIDEO
        if f_type == "video":
            stream = yt.streams.filter(
                res=quality,
                file_extension="mp4"
            ).first()
            filename = f"{safe_title}.mp4"

        # AUDIO
        else:
            stream = yt.streams.filter(
                only_audio=True
            ).first()
            filename = f"{safe_title}.mp3"

        if stream is None:
            flash("Selected quality not available. Try 360p or Audio.", "danger")
            return redirect(url_for("home"))

        stream.download(
            output_path=app.config["DOWNLOAD_FOLDER"],
            filename=filename
        )

        return send_from_directory(
            app.config["DOWNLOAD_FOLDER"],
            filename,
            as_attachment=True
        )

    except Exception as e:
        flash(f"Something went wrong: {str(e)}", "danger")
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
