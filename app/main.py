from fastapi import FastAPI

app = FastAPI(title="Rizal Subtitle Addon")

@app.get("/")
async def home():
    return {
        "status": "online"
    }
