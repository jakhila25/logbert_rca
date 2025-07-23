
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db import connect_to_database, disconnect_from_database, database
from schema import rca_results, RCAResult
import logging

# Set up logger
logger = logging.getLogger("uvicorn.error")
 
# FastAPI setup

app = FastAPI(title="RCA Service")

# CORS settings to allow all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

@app.get("/rca/latest", response_model=list[RCAResult])
async def get_latest_rca():
    query = rca_results.select().order_by(rca_results.c.logdate.desc())
    rows = await database.fetch_all(query)
    if not rows:
        logger.info("No RCA results found.")
        raise HTTPException(status_code=404, detail="No RCA results found.")
    logger.info(f"Returning {len(rows)} RCA result(s)")
    results = []
    for row in rows:
        row = dict(row)
        # Ensure events is a list of dicts, not strings
        if "events" in row and isinstance(row["events"], list):
            if row["events"] and isinstance(row["events"][0], str):
                row["events"] = [{"message": e} for e in row["events"]]
        results.append(row)
    return results


