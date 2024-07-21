from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from db import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer)
    query_date = Column(Date)
    name = Column(String)
    history = Column(String)
    total_played = Column(Integer)
    wins_home = Column(Integer)
    wins_away = Column(Integer)
    draws_home = Column(Integer)
    draws_away = Column(Integer)
    loses_home = Column(Integer)
    loses_away = Column(Integer)
    goals_for_home = Column(Integer)
    goals_for_away = Column(Integer)
    goals_against_home = Column(Integer)
    goals_against_away = Column(Integer)



class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    fixture = Column(Integer)
    match_date = Column(Date)
    team_home = Column(Integer)
    team_away = Column(Integer)
    result_predict = Column(String)
    result_real = Column(String)

    # TODO: Review FK
    # team_home = relationship("team_home", foreign_keys="Team.team_id")
    # team_away = relationship("team_away", foreign_keys="Team.team_id")



class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    num_requests = Column(Integer)