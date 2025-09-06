from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime

app = FastAPI(title="Astrology Compute API")

class IncludeFlags(BaseModel):
    lots: bool = False
    nodes: bool = False
    sect: bool = False
    visibility: bool = False

class CreateNatalChartRequest(BaseModel):
    date: str
    time: str
    timezone: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    house_system: Optional[str] = "whole_sign"
    zodiac: Optional[str] = "tropical"
    include: Optional[IncludeFlags] = IncludeFlags()

class CreateNatalChartResponse(BaseModel):
    chartId: str
    positions: Optional[List[dict]] = []

class ComputeTransitsRequest(BaseModel):
    chartId: str
    targetDateTime: str
    timezone: str
    orbDegrees: Optional[float] = 3.0

class TransitAspect(BaseModel):
    transitingPlanet: str
    natalPlanet: str
    type: str
    orbDegrees: float
    applying: bool

class ComputeTransitsResponse(BaseModel):
    chartId: str
    targetDateTime: str
    aspects: List[TransitAspect]
    transitingPositions: Optional[List[dict]] = []

@app.post("/natal-charts", response_model=CreateNatalChartResponse)
def create_natal_chart(body: CreateNatalChartRequest):
    cid = "chart_" + uuid.uuid4().hex[:10]
    return CreateNatalChartResponse(chartId=cid, positions=[])

@app.post("/transits", response_model=ComputeTransitsResponse)
def compute_transits(body: ComputeTransitsRequest):
    try:
        datetime.fromisoformat(body.targetDateTime.replace("Z",""))
    except ValueError:
        raise HTTPException(status_code=400, detail="targetDateTime must be ISO 8601")
    sample = [
        TransitAspect(
            transitingPlanet="Mars",
            natalPlanet="Venus",
            type="trine",
            orbDegrees=2.1,
            applying=True
        )
    ]
    return ComputeTransitsResponse(
        chartId=body.chartId,
        targetDateTime=body.targetDateTime,
        aspects=sample,
        transitingPositions=[]
    )
