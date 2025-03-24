import json
import pandas
import pygsheets

SHEET_URL = "https://docs.google.com/spreadsheets/d/1GbQKx2yOoD3YKk16v19zOgX5A18XVtiKbzps846vpmk/edit?gid=0#gid=0"

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
    return winrates

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
    return winrates

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
    return winrates

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
    return winrates

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
    return winrates

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

def formatMatchupData(enemyData, friendlyData):
    df = pandas.DataFrame(columns=["hero", "games_with", "games_against", "winrate_with", "winrate_against", "mvps_with", "mvps_against"])
    for i, hero in enumerate(enemyData):
        withData = friendlyData[hero]
        vsData = enemyData[hero]
        df.loc[i] = [
            hero,
            withData[1],
            vsData[1],
            withData[0],
            vsData[0],
            withData[2],
            vsData[2]
        ]
    return df

def formatBanData(allBans, ourBans, enemyBans):
    df = pandas.DataFrame(columns=["hero", "total_banned", "we_banned", "enemy_banned", "winrate_banned", "winrate_we_banned", "winrate_enemy_banned"])
    for i, hero in enumerate(allBans):
        banData = allBans.get(hero, [0,0])
        ourBanData = ourBans.get(hero, [0,0])
        enemyBanData = enemyBans.get(hero, [0,0])

        df.loc[i] = [
            hero,
            banData[1],
            ourBanData[1],
            enemyBanData[1],
            banData[0],
            ourBanData[0],
            enemyBanData[0],
        ]
    return df

def uploadData(sheet, df):
    gc = pygsheets.authorize(service_file='creds/sefeb20220208-7226846582b9.json')
    sh = gc.open_by_url(SHEET_URL)
    wks = sh[sheet]
    wks.set_dataframe(df, 'A1')

if __name__ == "__main__":
    data = {}
    with open(f"data/Xerronn_all_competitive.json") as inf:
        data = json.loads(inf.read())
    heroEnemyData = getHeroMatchupData(data)
    heroFriendlyData = getHeroTeamData(data)
    winratesDf = formatMatchupData(heroEnemyData, heroFriendlyData)
    # uploadData(0, winratesDf)

    allBans = getBanData(data)
    ourBans = getOurBanData(data)
    enemyBans = getEnemyBanData(data)
    bansDf = formatBanData(allBans, ourBans, enemyBans)
    uploadData(1, bansDf)

    # getAccuracyData(data)
    # print(getMVPCount(data))




