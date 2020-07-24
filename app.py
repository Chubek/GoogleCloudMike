from flask import Flask, render_template, request, g
from to_sheet import run_grab

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("request_button.html")


@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        form_result = request.form
        alert = run_grab(form_result.get("Name"),
                         True if form_result.get("Create") == 'on' else False,
                         form_result.get("ShareEmail"))

        return render_template("result.html", alert=alert)
