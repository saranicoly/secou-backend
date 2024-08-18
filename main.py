from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from elevationAPI import elevation, elevation_along_path
from calculate import calculate_route
from pydantic import BaseModel

app = FastAPI()

# Configurar CORS
origins = [
    "http://localhost:8100",  # Origem do seu frontend Ionic
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FloodRequest(BaseModel):
    street: str
    level: int

@app.post("/get_route", status_code=201)
def send_adresses(origin: str, destination: str, time: Optional[int] = None):
    print(f"Received data: origin={origin}, destination={destination}, time={time}")
    return calculate_route(origin, destination, time)

@app.post("/flooding", status_code=200)
def send_flooding(request: FloodRequest):
    if request.level < 0 or request.level > 5:
        raise HTTPException(status_code=400, detail="Invalid level")
    return {"message": "Flooding data received"}


@app.get("/api/google-maps-api-key")
async def get_google_maps_api_key():
    api_key = os.environ.get("GCP_KEY")
    if api_key:
        print(f"GCP_KEY found: {api_key}")
        return {"apiKey": api_key}
    else:
        print("GCP_KEY not found or is None")
        return {"apiKey": None}
