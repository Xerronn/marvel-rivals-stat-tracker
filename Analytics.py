import json
uidMapping = {
    956473791: "Jarod",
    868467988: "Zack",
    865128264: "Addy",
    1444480968: "Liz",
    1851358567: "Ethan",
    1129681929: "Hans"
}

heroIdMapping = {
    1011: "hulk",
    1014: "the punisher",
    1015: "storm",
    1016: "loki",
    1017: "human torch",
    1018: "doctor strange",
    1020: "mantis",
    1021: "hawkeye",
    1022: "captain america",
    1023: "rocket raccoon",
    1024: "hela",
    1025: "cloak & dagger",
    1026: "black panther",
    1027: "groot",
    1029: "magik",
    1030: "moon knight",
    1031: "luna snow",
    1032: "squirrel girl",
    1033: "black widow",
    1034: "iron man",
    1035: "venom",
    1036: "spider-man",
    1037: "magneto",
    1038: "scarlet witch",
    1039: "thor",
    1040: "mister fantastic",
    1041: "winter soldier",
    1042: "peni parker",
    1043: "star-lord",
    1045: "namor",
    1046: "adam warlock",
    1047: "jeff the land shark",
    1048: "psylocke",
    1049: "wolverine",
    1050: "invisible woman",
    1051: "the thing",
    1052: "iron fist"
}

def getBanData(data):
    # [loss, win, draw]
    heroes = {hero: [0, 0, 0] for hero in heroIdMapping.keys()}
    for match in data["match_history"]:
        win = 0
        for player in match["match_players"]:
            #filter to only us and see if we win
            if player["player_uid"] in uidMapping.keys():
                win = player["is_win"]
                break
        for ban in  match.get("dynamic_fields", {}).get("ban_pick_info", []):
            heroes[ban["hero_id"]][win] += 1

    winrates = {}
    for hero in heroes:
        heroWinrates = heroes[hero]
        total = heroWinrates[0] + heroWinrates[1] + heroWinrates[2]
        if total > 0:
            winrate = heroWinrates[1] / total
            winrates[heroIdMapping[hero]] = [round(winrate, 2), round(total, 2)]
    winrates = {k: v for k, v in sorted(winrates.items(), key=lambda item: item[1][0])}
    print(json.dumps(winrates, indent=4))

def getOurBanData(data):
    # [loss, win, draw]
    heroes = {hero: [0, 0, 0] for hero in heroIdMapping.keys()}
    for match in data["match_history"]:
        win = 0
        camp = 0
        for player in match["match_players"]:
            #filter to only us and see if we win
            if player["player_uid"] in uidMapping.keys():
                win = player["is_win"]
                camp = player["camp"]
                break
        for ban in match.get("dynamic_fields", {}).get("ban_pick_info", []):
            if ban["battle_side"] == camp:
                heroes[ban["hero_id"]][win] += 1

    winrates = {}
    for hero in heroes:
        heroWinrates = heroes[hero]
        total = heroWinrates[0] + heroWinrates[1] + heroWinrates[2]
        if total > 0:
            winrate = heroWinrates[1] / total
            winrates[heroIdMapping[hero]] = [round(winrate, 2), round(total, 2)]
    winrates = {k: v for k, v in sorted(winrates.items(), key=lambda item: item[1][0])}
    print(json.dumps(winrates, indent=4))

def getEnemyBanData(data):
    # [loss, win, draw]
    heroes = {hero: [0, 0, 0] for hero in heroIdMapping.keys()}
    for match in data["match_history"]:
        win = 0
        camp = 0
        for player in match["match_players"]:
            #filter to only us and see if we win
            if player["player_uid"] in uidMapping.keys():
                win = player["is_win"]
                camp = player["camp"]
                break
        for ban in match.get("dynamic_fields", {}).get("ban_pick_info", []):
            if ban["battle_side"] != camp:
                heroes[ban["hero_id"]][win] += 1

    winrates = {}
    for hero in heroes:
        heroWinrates = heroes[hero]
        total = heroWinrates[0] + heroWinrates[1] + heroWinrates[2]
        if total > 0:
            winrate = heroWinrates[1] / total
            winrates[heroIdMapping[hero]] = [round(winrate, 2), round(total, 2)]
    winrates = {k: v for k, v in sorted(winrates.items(), key=lambda item: item[1][0])}
    print(json.dumps(winrates, indent=4))

def getHeroMatchupData(data):
    heroes = {hero: {"winrates": [0, 0, 0], "mvps/svps": 0} for hero in heroIdMapping.keys()}
    for match in data["match_history"]:
        #drop all matches before 1/10
        if int(match["match_uid"].split("_")[1]) < 1736485200:
            continue
        mvp = match["mvp_uid"]
        svp = match["svp_uid"]
        for player in match["match_players"]:
            #filter out any of us
            if player["player_uid"] not in uidMapping.keys():
                #get total playtime so we can get the fraction of the game each hero was played
                totalPlaytime = 0
                for hero in player["player_heroes"]:
                    totalPlaytime += hero["play_time"]
                
                for hero in player["player_heroes"]:
                    heroPercentage = hero["play_time"] / totalPlaytime
                    heroes[hero["hero_id"]]["winrates"][player["is_win"]] += heroPercentage
                    if player["player_uid"] in [mvp, svp]:
                        heroes[hero["hero_id"]]["mvps/svps"] += heroPercentage
    winrates = {}
    for hero in heroes:
        heroWinrates = heroes[hero]["winrates"]
        total = heroWinrates[0] + heroWinrates[1] + heroWinrates[2]
        if total > 0:
            winrate = heroWinrates[0] / total
            winrates[heroIdMapping[hero]] = [round(winrate, 2), round(total, 2), round(heroes[hero]["mvps/svps"], 2)]
    winrates = {k: v for k, v in sorted(winrates.items(), key=lambda item: item[1][0])}
    print(json.dumps(winrates, indent=4))

def getHeroTeamData(data):
    heroes = {hero: {"winrates": [0, 0, 0], "mvps/svps": 0} for hero in heroIdMapping.keys()}
    for match in data["match_history"]:
        #drop all matches before 1/10
        if int(match["match_uid"].split("_")[1]) < 1736485200:
            continue
        mvp = match["mvp_uid"]
        svp = match["svp_uid"]
        for player in match["match_players"]:
            #only include us
            if player["player_uid"] in uidMapping.keys():
                #get total playtime so we can get the fraction of the game each hero was played
                totalPlaytime = 0
                for hero in player["player_heroes"]:
                    totalPlaytime += hero["play_time"]
                
                for hero in player["player_heroes"]:
                    heroPercentage = hero["play_time"] / totalPlaytime
                    heroes[hero["hero_id"]]["winrates"][player["is_win"]] += heroPercentage
                    if player["player_uid"] in [mvp, svp]:
                        heroes[hero["hero_id"]]["mvps/svps"] += heroPercentage
    winrates = {}
    for hero in heroes:
        heroWinrates = heroes[hero]["winrates"]
        total = heroWinrates[1] + heroWinrates[0] + heroWinrates[2]
        if total > 0:
            winrate = heroWinrates[1] / total
            winrates[heroIdMapping[hero]] = [round(winrate, 2), round(total, 2), round(heroes[hero]["mvps/svps"], 2)]
    winrates = {k: v for k, v in sorted(winrates.items(), key=lambda item: item[1][0])}
    print(json.dumps(winrates, indent=4))

def getAccuracyData(data):
    # [accuracy, totalDuration]
    accuracies = {player: [0, 0] for player in uidMapping.keys()}
    for match in data["match_history"]:
        for player in match["match_players"]:
            if player["player_uid"] in uidMapping.keys():
                for hero in player["player_heroes"]:
                    accuracies[player["player_uid"]][0] += hero["session_hit_rate"] * hero["play_time"]
                    accuracies[player["player_uid"]][1] += hero["play_time"]

    accuracies = {uidMapping[k]: round(v[0] / v[1], 2) for k, v in accuracies.items()}
    accuracies = {k: v for k, v in sorted(accuracies.items(), key=lambda item: item[1])}
    print(json.dumps(accuracies, indent=4))

def getMVPCount(data):
    mvps = {}
    for match in data["match_history"]:
        #drop all matches before 1/10
        if int(match["match_uid"].split("_")[1]) < 1736485200:
            continue
        mvp = uidMapping.get(match["mvp_uid"])
        svp = uidMapping.get(match["svp_uid"])
        if mvp is not None:
            if mvp in mvps:
                mvps[mvp] += 1
            else:
                mvps[mvp] = 1

        if svp is not None:
            if svp in mvps:
                mvps[svp] += 1
            else:
                mvps[svp] = 1
    return mvps

if __name__ == "__main__":
    data = {}
    with open(f"data/Xerronn_all_competitive.json") as inf:
        data = json.loads(inf.read())
    # print(getHeroMatchupData(data))
    # print(getMVPCount(data))
    # print(getHeroTeamData(data))
    # getBanData(data)
    # getOurBanData(data)
    # getEnemyBanData(data)
    getAccuracyData(data)



