from flask import Flask, redirect, render_template, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField
from wtforms.validators import DataRequired
import requests
import os
import re

from dotenv import load_dotenv

load_dotenv()

API_ENDPOINT = f"https://api.dictionaryapi.dev/api/v2/entries/en/<word>"


def call_endpoint(word: str):
    response = requests.get(API_ENDPOINT.replace("<word>", word))

    if response.status_code == 404:
        return False

    data = response.json()
    pronunciation = data[0]["phonetic"]
    definitions = []

    for word_entry in data:
        for word_meanings in word_entry["meanings"]:
            pos = word_meanings["partOfSpeech"]
            for meaning in word_meanings["definitions"]:
                meaning["type"] = pos
                definitions.append(meaning)
    return {
        "word": word,    
        "pronunciation": pronunciation, 
        "definitions": definitions 
    }



class SearchForm(FlaskForm):
    word = SearchField("", validators=[DataRequired()])
    search = SubmitField("Search", validators=[DataRequired()])


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
Bootstrap5(app)


@app.route("/", methods=["GET", "POST"])
def home():
    form = SearchForm()
    if form.validate_on_submit():
        word = form.word.data
        return redirect(url_for("define", word=word))
    return render_template("index.html", form=form)
    

@app.route("/definition/<word>")
def define(word):
    word = word.lower()
    is_invalid = False

    data = call_endpoint(word)
    if not data:
        is_invalid = (True, word)

    return render_template("response.html", is_invalid=is_invalid, data=data)


if __name__ == "__main__":
    app.run(debug=True)
