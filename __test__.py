from googleapiclient.discovery import build


SEARCH_ENGINE_ID = "006168594918175601863:t8oecxasips"
API_KEY = "AIzaSyCjuHRi_hJDXGBsGKSO4nTaz5k4EQ4K1WI"

service = build("customsearch", "v1", developerKey=API_KEY)

the_result = service.cse().list(q="tap AND water And Los Angeles", cx=SEARCH_ENGINE_ID).execute()

urls = []

for item in the_result.get("items"):
    urls.append(item.get("link").replace("www", "old"))

print(len(urls))