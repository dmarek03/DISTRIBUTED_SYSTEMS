import os
import httpx
import uvicorn
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from model import Match, Team, TeamStat
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

API_KEY = os.getenv('API_KEY')
MATCH_DAY_URL = os.getenv('MATCH_DAY_URL')
STANDINGS_URL = os.getenv('STANDINGS_URL')
headers = {'X-Auth-Token': API_KEY}


app = FastAPI()

origins = [
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def root():
    return FileResponse('../frontend/build/index.html')


@app.get('/v1/matches/', response_model=list[Match])
async def get_matches(league_name: str, season: int, matchday: int, champions_league_stage: str | None = None):
    url = MATCH_DAY_URL.format(league_name=league_name)
    params = {'season': season, 'matchday': matchday}

    if champions_league_stage:
        params['stage'] = champions_league_stage

    async with httpx.AsyncClient() as a_client:
        try:
            response = await a_client.get(url, params=params, headers=headers)
            response.raise_for_status()

        except httpx.HTTPStatusError:
           raise HTTPException(status_code=response.status_code, detail='Error downloading matches data')

        except httpx.RequestError:
            raise HTTPException(
                status_code=response.status_code,
                detail='Connection error during downloading matches data'
            )

    data = response.json()
    matches = []
    for d in data.get('matches'):
        home_team = Team(name=d['homeTeam']['name'], logo=d['homeTeam']['crest'])
        away_team = Team(name=d['awayTeam']['name'], logo=d['awayTeam']['crest'])
        result = f"{d['score']['fullTime']['home']}:{d['score']['fullTime']['away']}"
        match_datetime = datetime.strptime(d['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
        formatted_match_datetime = match_datetime.strftime("%Y-%m-%d %H:%M")

        matches.append(
            Match(home_team=home_team, away_team=away_team, result=result, datetime=formatted_match_datetime))

    return matches


@app.get('/v1/standings/', response_model=list[TeamStat])
async def get_season_standings(league_name: str, season: int, matchday: int, order_by: str = 'points',
                               desc: bool = False, champions_league_stage: str | None = None):
    url = STANDINGS_URL.format(league_name=league_name)
    params = {'season': season, 'matchday': matchday}

    if champions_league_stage:
        params['stage'] = champions_league_stage

    async with httpx.AsyncClient() as a_client:

        try:
            response = await a_client.get(url=url, params=params, headers=headers)

        except httpx.HTTPStatusError:
            HTTPException(status_code=response.status_code, detail="Error downloading standings data")

        except httpx.RequestError:
            HTTPException(status_code=response.status_code, detail="Connection error during downloading standings data")

    data = response.json()

    season_table = []

    for team_stats in data['standings'][0]['table']:
        team_name = team_stats['team']['name']
        logo = team_stats['team']['crest']

        played_games = int(team_stats['playedGames'])
        form = team_stats['form']
        won = int(team_stats['won'])
        draw = int(team_stats['draw'])
        lost = int(team_stats['lost'])
        points = int(team_stats['points'])
        goals_for = int(team_stats['goalsFor'])
        goals_against = int(team_stats['goalsAgainst'])
        goal_diff = int(team_stats['goalDifference'])

        season_table.append(
            TeamStat(
                name=team_name,
                logo=logo,
                played_games=played_games,
                form=form,
                won=won,
                draw=draw,
                lost=lost,
                points=points,
                goals_for=goals_for,
                goals_against=goals_against,
                goal_diff=goal_diff
            )
        )

    return sorted(season_table, key=lambda x: getattr(x, order_by), reverse=desc)


if __name__ == '__main__':
    uvicorn.run('simple_app:app', host="127.0.0.1", port=8000, reload=True)
