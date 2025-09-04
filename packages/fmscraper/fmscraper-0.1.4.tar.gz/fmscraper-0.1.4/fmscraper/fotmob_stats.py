import requests
from fmscraper.xmas_generator import generate_xmas_header

class FotMobStats:
    def __init__(self,league_id,season):
        self.url = "https://www.fotmob.com/api"
        self.league_id = league_id
        self.season = season.replace("-", "%2F")
        self.matchdetails_url = self.url+f'/matchDetails?matchId='
        self.leagues_url = self.url+f'/leagues?id={self.league_id}'
        self.team_url = self.url+f'/teams?id='
        self.player_url = self.url+f'/playerStats?playerId='
        self.headers = {
            "x-mas": generate_xmas_header(self.matchdetails_url)
        }
        self.match_content_types = ['matchFacts', 'stats', 'playerStats',
                              'shotmap','lineup']

    def get_json_content(self, url):
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()


    def get_player_stats(self,player_id,season_id):
        # current season_id is always 0, last season is 1, etc.
        url = self.player_url+str(player_id)+f'&seasonId={season_id}-0&isFirstSeason=false'
        data = self.get_json_content(url)
        return data


    def get_team_stats(self,team_id):
        url = self.team_url+str(team_id)
        data = self.get_json_content(url)
        return data


    def get_matches_list(self,team_or_all):
        data = self.get_json_content(self.leagues_url+f"&season={self.season}")
        games_list = data['matches']['allMatches']
        if team_or_all == "all":
            game_ids = [game['id'] for game in games_list]
        else:
            assert team_or_all.lower() in self.get_available_teams().keys()
            team = team_or_all.lower().replace(" ","-")
            game_ids = [game['id'] for game in games_list if team in game['pageUrl']]
        return game_ids


    def get_season_stats(self,players_or_teams):
        data = self.get_json_content(self.leagues_url+f"&season={self.season}")
        try:
            stats_json_list = [stat['fetchAllUrl'] for stat in data['stats'][players_or_teams]]
            season_data = [requests.get(stat).json()['TopLists'][0] for stat in stats_json_list]
            return season_data
        except KeyError:
            return "Incorrect players_or_teams value. Please pick either 'players' or 'teams'"

    def get_match_details(self, match_id,content_type:str="stats"):
        data = self.get_json_content(url=self.matchdetails_url + str(match_id))
        assert content_type in self.match_content_types
        home = data['general']['homeTeam']
        away = data['general']['awayTeam']
        return {"home":home['name'], "home_id": home['id'], "away":away['name'], "away_id": away['id']} | data['content'][content_type]

    def get_available_teams(self):
        data = self.get_json_content(url=self.leagues_url + f"&season={self.season}&tab=overview&type=league")
        try:
            teams = data['table'][0]['data']['table']['all']
        except KeyError as e:
            teams = data['table'][0]['data']['tables'][2]['table']['xg']
        teams_dict = {team['name'].lower(): {"name": team['name'].replace(" ", "-").lower(),
                                             "id": team['id']} for team in teams}
        return teams_dict


if __name__ == "__main__":
    bundesliga_stats = FotMobStats(league_id=38,season="2024-2025")
    # for value in staty.values():
    #     print(value)
