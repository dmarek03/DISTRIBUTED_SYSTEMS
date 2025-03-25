from datetime import datetime

from pydantic import BaseModel, Field


class Team(BaseModel):
    name: str
    logo: str


class TeamStat(Team):
    played_games: int
    form: str
    won: int
    draw: int
    lost: int
    points: int
    goals_for: int
    goals_against: int
    goal_diff: int


class Match(BaseModel):
    home_team: Team
    away_team: Team
    result: str
    datetime: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M')
        }
