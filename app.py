


from datetime import datetime
import json
import os
import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


load_dotenv()

# Load a small language model for reasoning
MODEL_NAME = "distilgpt2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
model.eval()

app = FastAPI(title="RCA API Service")


class RCAResult(BaseModel):
    id: int
    filename: str
    app_id: str
    score: Optional[float]
    z_score: Optional[float]
    undetected_ratio: Optional[float]
    status: Optional[str]
    events: Optional[List[dict]]
    explanation: Optional[str]
    logdate: Optional[str]


# Async get_rca_results function using asyncpg and ASYNC_DATABASE_URL


# Use the same connection string logic as in sql.py
ASYNC_DATABASE_URL = os.getenv("DATABASE_URI")
if not ASYNC_DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URI not found in environment variables. Please set it in your .env file.")
if ASYNC_DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace(
        "postgresql://", "postgresql+asyncpg://")



def generate_prompt(event_templates):
    prompt = "The system encountered a failure. Below are the key log events preceding the anomaly:\n\n"
    for i, event in enumerate(event_templates, 1):
        prompt += f"{i}. {json.dumps(event, ensure_ascii=False)}\n"
    prompt += "\nBased on the above log events, identify the most likely root cause of the issue.\n"
    prompt += "Explain the cause in one or two sentences, using technical reasoning if possible.\n"

    # Use a small language model to generate reasoning
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    attention_mask = torch.ones_like(input_ids)
    with torch.no_grad():
        output = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=input_ids.shape[1]+60,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id
        )
    generated = tokenizer.decode(output[0][input_ids.shape[1]:], skip_special_tokens=True)
    reasoning = generated.strip()
    return prompt + "\nAI Reasoning: " + reasoning



async def get_rca_results():
    """
    Fetch all RCA results from the rca_results table as a list of dicts (async).
    Uses ASYNC_DATABASE_URL for connection.
    """
    # Remove sqlalchemy+asyncpg prefix for asyncpg
    pg_url = ASYNC_DATABASE_URL.replace(
        "postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(pg_url)
    try:
        rows = await conn.fetch("SELECT * FROM rca_results ORDER BY logdate DESC LIMIT 1;")
        results = []
        for row in rows:
            row_dict = dict(row)
            # Parse events if it's a string
            events = row_dict.get("events")
            if isinstance(events, str):
                try:
                    row_dict["events"] = json.loads(events)
                except Exception:
                    row_dict["events"] = None
            # Convert logdate to ISO string if it's a datetime
            logdate = row_dict.get("logdate")
            if isinstance(logdate, datetime):
                row_dict["logdate"] = logdate.isoformat()
            results.append(row_dict)
        return results
    finally:
        await conn.close()


@app.get("/rca/", response_model=List[RCAResult])
async def get_rca():
    try:
        rows = await get_rca_results()

        if rows:
            for row in rows:
                event_templates = row.get("events") if row.get("events") else []
                prompt = generate_prompt(event_templates)
                row["explanation"] = prompt
            return [RCAResult(**row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
