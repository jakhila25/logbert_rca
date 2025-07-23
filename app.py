
from fastapi import FastAPI, HTTPException
from sql import database
from schema import rca_results, RCAResult

# FastAPI setup
app = FastAPI(title="RCA Service")



@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

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
