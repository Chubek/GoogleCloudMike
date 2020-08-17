import pandas as pd

hello = [{"gimme": "a man after midnight"}, {"gimme": "a jew after midnight"}]

df = pd.DataFrame.from_records(hello)

print(df.head())