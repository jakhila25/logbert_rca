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
    Column("id", String, primary_key=True),
    Column("filename", String, nullable=False, index=True),
    Column("rootcause", Text, nullable=True),
    Column("events", JSON, nullable=True),
    Column("logdate", DateTime, default=func.now(), nullable=False),
    Column("ai_explanation", Text, nullable=True),
)

# ========== Pydantic Schema ==========
class RCAResult(BaseModel):
    filename: str
    rootcause: str
    events: Optional[List[dict]] = Field(default_factory=list)
    logdate: Optional[datetime] = Field(default_factory=datetime.utcnow)
    ai_explanation: Optional[str] = None

    class Config:
        orm_mode = True
