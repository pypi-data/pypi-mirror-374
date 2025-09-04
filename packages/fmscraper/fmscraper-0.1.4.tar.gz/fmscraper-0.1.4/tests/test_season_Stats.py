from fmscraper import FotMobStats
import pandas as pd
from collections import defaultdict

# stats = FotMobStats(league_id=38,season='2024-2025').get_season_stats('players')
# players_stats = []
#
# for stat in stats:
#     stat_name = stat['StatName']
#     substat_name = stat['Subtitle']
#     lista = stat['StatList']
#     for l in lista:
#         l[stat_name] = l.pop('StatValue')
#         l[substat_name] = l.pop('SubStatValue')
#         players_stats.append(l)
#
def merge_dicts(data):
    merged = defaultdict(dict)
    for entry in data:
        pid = entry.get("ParticipantName")
        if pid is not None:
            merged[pid].update(entry)
    return list(merged.values())


# df = pd.DataFrame(merge_dicts(players_stats)).fillna(0)
# df["90's played"] = round(df['MinutesPlayed']/90,2)
# df.to_excel('staty.xlsx')
stats = FotMobStats(league_id=38,season='2024-2025').get_season_stats('teams')
team_stats = []
for stat in stats:
    stat_name = stat['StatName']
    substat_name = stat['Subtitle']
    lista = stat['StatList']
    for l in lista:
        l[stat_name] = l.pop('StatValue')
        l[substat_name] = l.pop('SubStatValue')
        team_stats.append(l)

pd.DataFrame(merge_dicts(team_stats)).to_excel("team_stats.xlsx")