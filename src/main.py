import os
import pprint

import pandas as pd
import requests

API_KEY = os.getenv("API_KEY")

steam_url = "https://steampowered.com/api/appdetails"

games = [
    '730'
]

r = requests.get(
    steam_url,
    params={"appids": 730},
    timeout=15,
)

# App Id, genres, categories, price, release data, description

data = []

for game_id in games:
    try:
        r = requests.get(
            steam_url,
            params={"appids": game_id},
            timeout=15,
        )

        request_data = r.json()[str(game_id)]["data"]
        data.append(request_data)
    except Exception as e:
        print("Error getting game!")

pprint.pprint(data)


df = pd.DataFrame()
