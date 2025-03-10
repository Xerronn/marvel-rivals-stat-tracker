import json
import requests

API = "https://marvelrivalsapi.com"
KEY = open("creds/key.txt", 'r').read()

def UpdatePlayerData(username):
    endpoint = f"{API}/api/v1/player/{username}/update"
    headers = {'x-api-key': KEY}
    request = requests.get(endpoint, headers=headers)
    return request.json().get("success", False)

def QueryMatchHistory(username, season, skip):
    #game mode 2 is comp
    endpoint = f"{API}/api/v1/player/{username}/match-history?season={season}&skip={skip}&game_mode=2"
    headers = {'x-api-key': KEY}
    request = requests.get(endpoint, headers=headers)
    return request.json()

def QueryAllMatchHistory(username):
    # if not UpdatePlayerData(username):
    #      raise Exception("Failed to update player data")
    allMatches = []
    for season in [0, 1, 1.5]:
        matchCounter = 0
        while True:
            data = QueryMatchHistory(username, season, matchCounter)
            print(data)
            allMatches.extend(data["match_history"])
            print(len(allMatches))
            if len(data["match_history"]) < 20:
                break
            matchCounter += 20
    with open(f"data/{username}.json", 'w') as inf:
        outData = {"match_history": allMatches}
        inf.write(json.dumps(outData, indent=4))

def QueryMatchData(matchId):
    retries = 0
    while retries < 15:
        endpoint = f"{API}/api/v1/match/{matchId}"
        headers = {'x-api-key': KEY}
        request = requests.get(endpoint, headers=headers)
        data = request.json()
        if data.get("status", 200) == 200:
            return data

        print("Retrying...")
        retries += 1

#must be called after QueryAllMatchHistory
def QueryAllMatchData(username):
    data = {}
    with open(f"data/{username}.json") as inf:
        data = json.loads(inf.read())

    allMatches = []
    for i, match in enumerate(data["match_history"]):
       print(i)
       matchData = QueryMatchData(match["match_uid"])
       allMatches.append(matchData["match_details"])

    with open(f"data/{username}_all_competitive.json", 'w') as inf:
        outData = {"match_history": allMatches}
        inf.write(json.dumps(outData, indent=4))

def GetHeroIdMapping():
    endpoint = f"{API}/api/v1/heroes"
    headers = {'x-api-key': KEY}
    request = requests.get(endpoint, headers=headers)
    out = {}
    for hero in request.json():
        out[hero["id"]] = hero["name"]
    print(json.dumps(out, indent=4))

if __name__ == "__main__":
    QueryAllMatchHistory("Xerronn")
    QueryAllMatchData("Xerronn")