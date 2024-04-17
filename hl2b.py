# -*- coding: utf-8 -*-

import requests
import os
import Levenshtein
import csv
import pprint
import re

from io import StringIO

REQUEST_ID = ""
OUTPUT_FILE = 'game_info.csv'
username = ""
country_code = "us"
nonce = ""
tag_filter = "Story Rich"

def search_howlongtobeat(query_string):
    url = "https://howlongtobeat.com/api/search"
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://howlongtobeat.com",
        "Content-Type": "application/json",
        "Origin": "https://howlongtobeat.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers"
    }
    data = {
        "searchType": "games",
        "searchTerms": query_string.split(),
        "searchPage": 1,
        "size": 20,
        "searchOptions": {
            "games": {
                "userId": 0,
                "platform": "",
                "sortCategory": "popular",
                "rangeCategory": "main",
                "rangeTime": {"min": None, "max": None},
                "gameplay": {"perspective": "", "flow": "", "genre": ""},
                "rangeYear": {"min": "", "max": ""},
                "modifier": ""
            },
            "users": {"sortCategory": "postcount"},
            "lists": {"sortCategory": "follows"},
            "filter": "",
            "sort": 0,
            "randomizer": 0
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code >= 300:
        print("Problem getting results from How Long To Beat")
        return {}
    return response.json()

def fetch_steam_data(username, country_code, nonce):
    url = "https://www.lorenzostanco.com/lab/steam/proxy.php"
    params = {
        "t": "user_library",
        "u": username,
        "cc": country_code,
        "nonce": nonce
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Accept": "*/*",
        "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "https://www.lorenzostanco.com/lab/steam/"
    }

    response = requests.get(url, params=params, headers=headers)
    if response.ok:
        return response.json()
    else:
        return None

def fetch_steam_game_store_data(profile, app_ids, request_id, nonce):
    url = "https://www.lorenzostanco.com/lab/steam/proxy.php"
    params = {
        "t": "game_store_json",
        "profile": profile,
        "app_ids": app_ids,
        "request_id": request_id,
        "nonce": nonce
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Accept": "*/*",
        "Accept-Language": "pt-PT,pt;q=0.8,en;q=0.5,en-US;q=0.3",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "https://www.lorenzostanco.com/lab/steam/u/" + profile
    }

    response = requests.get(url, params=params, headers=headers)
    if response.ok:
        return response.json()
    else:
        return None

def process_steam_data(steam_data, username, country_code, nonce):    
    if steam_data is None:
        return None

    processed_data = []
    for i in range(0, len(steam_data), 50):
        batch_games = steam_data[i:i+50]
        app_ids = []
        for game in batch_games:
            app_ids.append(str(game["app_id"]) if "app_id" in game else str(game["game_id"]))
        app_ids_list = ','.join(app_ids)
        game_store_data = fetch_steam_game_store_data(username, app_ids_list, REQUEST_ID, nonce)
        games_info = game_store_data.get("games", [])
        if games_info is None:
            print("No result for app_ids" + str(app_ids))
        else:
            processed_data.extend(games_info)
    return processed_data

steam_data = fetch_steam_data(username, country_code, nonce)
processed_data = process_steam_data(steam_data, username, country_code, nonce)

os.system("cls")
print("##########################")
print("Total number of games: " + str(len(steam_data)))
print("Filtering by " + tag_filter)
filtered_data = [game for game in processed_data if tag_filter in game['tags']]
print("Number of filtered games: " + str(len(filtered_data)))

def validatedGet(variable, field):
    value = variable.get(field, 0)
    if value is None:
        value = 0
    elif type(value) is str:
        value = int(value)
    return value

def clean_name(name):
    name = name.replace('™', '')
    name = name.replace('®', '')
    return name

def minimal_info(game):
    return {"name": game["app_name"], "metascore": validatedGet(game, "metascore"), "userscore": validatedGet(game, "userscore"), "userscore_count": validatedGet(game, "userscore_count")}

minimal_game_info = [minimal_info(game) for game in filtered_data]

def find_closest_game(game_name, data):
    closest_game = None
    min_distance = float('inf')

    for game in data:
        distance = Levenshtein.distance(game_name.lower(), game["game_name"].lower())
        if distance < min_distance:
            min_distance = distance
            closest_game = game

    return closest_game

def seconds_to_hours_minutes(seconds):
    if type(seconds) is str:
        seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02}h {minutes:02}m"

minimal_game_info = sorted(minimal_game_info, key = lambda x: x["metascore"] if x["metascore"] > 0 else (x["userscore"] if (x["userscore"] is not None) and ((x["userscore_count"] if x["userscore_count"] is not None else 0) > 1000) else 0), reverse=True)
for game in minimal_game_info:
    game_name = clean_name(game["name"]).lower()
    print("Searching for %s in HL2B" % game_name)
    resp = search_howlongtobeat(game_name)
    game_data = resp["data"]
    my_game = find_closest_game(game_name, game_data)
    if not my_game:
        print("Couldn't find %s in the How Long to Beat Database" % game["name"])
        game_name = game_name.split(" - ")[0]
        game_name = game_name.replace("edition", "")        
        game_name = game_name.replace("game of the year", "goty")
        game_name = game_name.replace(":", " ")
        game_name = game_name.replace("&", "and")
        pattern = r"\(\d{4}\)"
        game_name = re.sub(pattern, "", game_name)
        print("Searching again in HL2B as: " + game_name)
        resp = search_howlongtobeat(game_name)
        game_data = resp["data"]
        my_game = find_closest_game(game_name, game_data)

    if not my_game:
        print("Couldn't find %s in the How Long to Beat Database" % game_name)
        game["duration"] = "00h 00m"
    else:
        game["duration"] = seconds_to_hours_minutes(my_game["comp_main"])
        print("Completion time: " + game["duration"])
    

keys = ["name","metascore","userscore","userscore_count","duration"]

pprint.pprint(minimal_game_info)
with open(OUTPUT_FILE, 'w', newline='', encoding='utf8') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(minimal_game_info)