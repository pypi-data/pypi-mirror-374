from fmscraper import FotMobStats
import matplotlib.pyplot as plt
import numpy as np

bundesliga_stats = FotMobStats(league_id=38, season="2024-2025")
mecze = bundesliga_stats.get_matches_list(team_or_all="austria wien")
xG_Austria = []
xGA_Austria = []

for mecz in mecze:
    staty_meczu = bundesliga_stats.get_match_details(match_id=mecz, content_type='stats')
    if staty_meczu['home_id'] == 10011:
        xG_Austria.append(float(staty_meczu['Periods']['All']['stats'][0]['stats'][1]['stats'][1]))
        xGA_Austria.append(float(staty_meczu['Periods']['All']['stats'][0]['stats'][1]['stats'][0]))
    else:
        xG_Austria.append(float(staty_meczu['Periods']['All']['stats'][0]['stats'][1]['stats'][0]))
        xGA_Austria.append(float(staty_meczu['Periods']['All']['stats'][0]['stats'][1]['stats'][1]))

xG_Austria = np.array(xG_Austria)
xGA_Austria = np.array(xGA_Austria)

plt.scatter(xGA_Austria, xG_Austria, label='Matches')
min_val = min(np.min(xG_Austria), np.min(xGA_Austria))
max_val = max(np.max(xG_Austria), np.max(xGA_Austria))

plt.plot([min_val, max_val], [min_val, max_val], color='black')
plt.axvline(x=1.5, color='gray', linestyle='--', linewidth=1) #try to make this a mean

# Horizontal line at y = 1.5
plt.axhline(y=1.5, color='gray', linestyle='--', linewidth=1) #try to make this a mean

plt.gca().invert_yaxis()
plt.xlabel('xG')
plt.ylabel('xGA')
plt.title('xG vs xGA for every Austria game')
plt.show()