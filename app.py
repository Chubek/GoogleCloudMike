import os

import LivingWaterScrape

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    LivingWaterScrape.living_water_threaded()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
