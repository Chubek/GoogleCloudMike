from rake_nltk import Rake
import re
import pandas as pd

r = Rake()
r.extract_keywords_from_text("I was drinking tap water in Phoenix, Arizona the other day and I noticed that \
                             the water is pretty salty. It's true about all arid regions in the United States at least, \
                             aridity brings salty drinking water.")

words = r.get_ranked_phrases()

words.append("colonel los angeles")

print(words[0])

pattern = re.compile("los angeles")

for word in words:
    print(pattern.search(word))

dict = [{"hello": ["py", "chi"], "hell": "tie"}, {"hello": "sie", "hell": "hi"}]

df = pd.DataFrame.from_records(dict)


print(df.head())