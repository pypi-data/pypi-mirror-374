from fmscraper import FotMobStats
import pandas as pd

stats = FotMobStats(league_id=38,season="2024-2025")

# player_ids = list(pd.read_excel("staty.xlsx")['ParticiantId'])

# pd.DataFrame([stats.get_player_stats(id) for id in player_ids]).to_excel("player_stats.xlsx")

otar_Staty = stats.get_player_stats(player_id=652954,season_id=1)['statsSection']['items']
print(otar_Staty)
# sub = {k: stats.get_player_stats(652954)[k] for k in ('mainLeague', 'traits','statSeasons')}
# print(sub)