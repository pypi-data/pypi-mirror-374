# FMScraper

FMScraper is a web scraping tool that uses requests for HTTP handling. This repository enables efficient extraction of data from [FotMob](https://www.fotmob.com/).

Inspired by: [Webscraper-PremData](https://github.com/deanpatel2/Webscraper-PremData/tree/main) and [scraping-football-sites](https://github.com/axelbol/scraping-football-sites/tree/main)

## Overview
FMScraper is a web scraping tool designed to extract comprehensive football match statistics and data from [FotMob](https://www.fotmob.com/), a popular platform for football statistics, live scores, and match analysis. The tool automates the data collection process, handling JavaScript-driven content and dynamic page layouts that traditional scraping methods cannot access.

## Features

- Scrapes match info from FotMob
- Extracts data for specific leagues, seasons, and matchweeks
- Provides easily exportable or processable match data for further analysis.

## Requirements

- Python 3.8+
- [requests](https://pypi.org/project/requests/)

## Disclaimer
For educational and research purposes only. Do not use it commercially.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MieszkoPugowski/FMScraper.git
cd FMScraper
```

2. Install using pip:
```bash
pip install fmscraper
```
## Example usage

```python
from fmscraper import FotMobStats 

bundesliga_stats = FotMobStats(league_id=38,season="2024-2025")
game_ids = bundesliga_stats.get_matches_list(team_or_all='all')

first_game = game_ids[0]

# List of all shots in a game
shotlist = bundesliga_stats.get_match_details(match_id=first_game,
                                                content_type="shotmap")
print(shotlist)
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue.


