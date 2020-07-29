from rake_nltk import Rake
import re
import pandas as pd

text = "In the Netherlands the price for our tap water is regulated at approximately 1 Euro per cubic metre (or 1000L of water). I rarely see people drinking flat bottled water and I can't remember when I last bought a bottle of water. The adoption of reusable bottles here has skyrocketed since some university students managed to make their bottle the fashionable item of the moment."

pattern = re.compile(rf"\b(?=\w)Netherlands|netherlands\b(?!\w)")

print(bool(pattern.search(text)))