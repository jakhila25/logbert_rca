
from fastapi import FastAPI, HTTPException
from db import connect_to_database, disconnect_from_database, database
from schema import rca_results, RCAResult
import logging

# Set up logger
logger = logging.getLogger("uvicorn.error")
 
# FastAPI setup
app = FastAPI(title="RCA Service")


# Startup event to initialize database connection
@app.on_event("startup")
async def startup():
    try:
        await connect_to_database()
        logger.info("Database connected successfully.")
        
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")

# Shutdown event to close database connection
@app.on_event("shutdown")
async def shutdown():
    try:
        await disconnect_from_database()
        logger.info("Database disconnected successfully.")
    except Exception as e:
        logger.error(f"Error disconnecting from the database: {e}")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/rca/latest", response_model=RCAResult)
async def get_latest_rca():
    query = rca_results.select().order_by(rca_results.c.logdate.desc()).limit(1)
    row = await database.fetch_one(query)
    if not row:
        raise HTTPException(status_code=404, detail="No RCA results found.")
    # Patch: ensure rootcause is a string for Pydantic validation
    if "rootcause" in row and row["rootcause"] is None:
        row = dict(row)
        row["rootcause"] = ""
    return row
