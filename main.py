import argparse
import requests


'''
1) Get matchups from kicktipp
2) Get odds from oddsapi or kicktipp
3) Match kicktipp matchup with oddsapivia teams.json and home_team/away_team in request, store in matchup dict?
4) Calculate result that yields the highest expected return


'''





#TEMP to not use all 500 API requests during development
USE_LOCAL_DATA = False
import json
data = 'data.json'
with open (data, 'r') as f:
	odds_response = json.load(f)
	#USE_LOCAL_DATA = True


# Obtain the api key that was passed in from the command line
parser = argparse.ArgumentParser(description='Sample V4')
parser.add_argument('--api-key', type=str, default='')
args = parser.parse_args()


API_KEY = args.api_key or 'YOUR_API_KEY'
SPORT = 'soccer_germany_bundesliga' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports
REGIONS = 'eu' # uk | us | eu | au. Multiple can be specified if comma delimited
MARKETS = 'h2h,totals' # h2h | spreads | totals. Multiple can be specified if comma delimited
ODDS_FORMAT = 'decimal' # decimal | american
DATE_FORMAT = 'iso' # iso | unix

sports_response = requests.get('https://api.the-odds-api.com/v4/sports', params={
	'api_key': API_KEY
})

if sports_response.status_code != 200:
	print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')
	pass
else:
	print('List of in season sports:', sports_response.json())
	


if not USE_LOCAL_DATA:
	sports_response = requests.get('https://api.the-odds-api.com/v4/sports', params={
		'api_key': API_KEY
	})

	if sports_response.status_code != 200:
		print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

	else:
		print('List of in season sports:', sports_response.json())

	odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds', params={
		'api_key': API_KEY,
		'regions': REGIONS,
		'markets': MARKETS,
		'oddsFormat': ODDS_FORMAT,
		'dateFormat': DATE_FORMAT,
	})

	if odds_response.status_code != 200:
		print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

	else:
		odds_json = odds_response.json()
		print('Number of events:', len(odds_json))
		print(odds_json)

		# Check the usage quota
		print('Remaining requests', odds_response.headers['x-requests-remaining'])
		print('Used requests', odds_response.headers['x-requests-used'])
		print(odds_response)
