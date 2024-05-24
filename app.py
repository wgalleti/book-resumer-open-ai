import os

import openai
import pyttsx3
from flask import Flask, request, render_template, send_from_directory

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
engine = pyttsx3.init()
engine.setProperty("rate", 200)

AUDIO_FOLDER = "static/audio"
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)


def get_book_summary(title, author=None):
    prompt = f"Faz um resumo para leitura do livro '{title}'"
    if author:
        prompt += f" escrito por {author}."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente que gera resumos de livros.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return None, str(e)


def generate_audio(summary):
    audio_file_path = os.path.join(AUDIO_FOLDER, "summary.mp3")
    engine.save_to_file(summary, audio_file_path)
    engine.runAndWait()
    return audio_file_path


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        title = request.form["title"]
        author = request.form.get("author")

        summary = get_book_summary(title, author)

        audio_url = None
        if "audio" in request.form:
            audio_file_path = generate_audio(summary)
            audio_url = f"/{audio_file_path}"

        return render_template("index.html", summary=summary, audio_url=audio_url)

    return render_template("index.html")


@app.route("/static/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
