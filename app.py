from flask import Flask, render_template
from to_sheet import run_grab

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("request_button.html")


@app.context_processor
def utility_processor():
    def run_task():
        run_grab()

