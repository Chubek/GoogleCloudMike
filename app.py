import os

import LivingWaterScrape

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    print("Server triggered")
    LivingWaterScrape.living_water_threaded()
    return "Function started!"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
