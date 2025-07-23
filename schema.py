from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# sql.py

import sqlalchemy

from sqlalchemy import (
    Table, Column, String, Integer, DateTime, ForeignKey, Text, func, JSON
)
from db import metadata


rca_results = Table(
    "rca_results",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("filename", String, nullable=False, index=True),
    Column("app_id", String, nullable=False),
    Column("score", sqlalchemy.Numeric, nullable=True),
    Column("z_score", sqlalchemy.Numeric, nullable=True),
    Column("undetected_ratio", sqlalchemy.Numeric, nullable=True),
    Column("status", String, nullable=True),
    Column("events", JSON, nullable=True),
    Column("explanation", Text, nullable=True),
    Column("logdate", DateTime(timezone=True), default=func.now(), nullable=False),
    schema="trans"
)

# ========== Pydantic Schema ==========
class RCAResult(BaseModel):
    id: int
    filename: str
    app_id: str
    score: Optional[float] = None
    z_score: Optional[float] = None
    undetected_ratio: Optional[float] = None
    status: Optional[str] = None
    events: Optional[List[dict]] = Field(default_factory=list)
    explanation: Optional[str] = None
    logdate: Optional[datetime] = None

    class Config:
        orm_mode = True
