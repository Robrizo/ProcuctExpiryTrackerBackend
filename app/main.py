from fastapi import FastAPI

app = FastAPI(
    title="Product Expiry Tracker API",
    description="REST API for household product tracking and 7-day expiry notifications",
    version="1.0.0"
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}