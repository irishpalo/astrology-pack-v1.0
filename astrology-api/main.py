from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo  # Python 3.9+
from skyfield.api import load
from skyfield.framelib import ecliptic_frame

app = FastAPI(title="Astrology Compute API")

# ============================
# Data models
# ============================
class IncludeFlags(BaseModel):
    lots: bool = False
    nodes: bool = False
    sect: bool = False
    visibility: bool = False

class CreateNatalChartRequest(BaseModel):
    date: str                      # "YYYY-MM-DD"
    time: str                      # "HH:MM[:SS]"
    timezone: str                  # e.g., "Africa/Johannesburg"
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
    targetDateTime: str            # ISO 8601 or "YYYY-MM-DDTHH:MM[:SS]"
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

# ============================
# Ephemeris (loaded once)
# ============================
TS = load.timescale()
EPH = load("de421.bsp")  # downloads on first use
EARTH = EPH["earth"]

ZODIAC = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANETS = {
    "Sun": EPH["sun"],
    "Moon": EPH["moon"],
    "Mercury": EPH["mercury"],
    "Venus": EPH["venus"],
    "Mars": EPH["mars"],
    "Jupiter": EPH["jupiter barycenter"],
    "Saturn": EPH["saturn barycenter"],
}

# ============================
# Helpers
# ============================
def to_dt(date_str: str, time_str: str, tz_name: str) -> datetime:
    """
    Parse a local date/time in the given IANA timezone and return an aware UTC datetime.
    """
    # Allow "HH:MM" or "HH:MM:SS"
    if len(time_str) == 5:
        time_str += ":00"

    try:
        naive_local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="date/time must be ISO (YYYY-MM-DD / HH:MM[:SS])")

    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {tz_name}")

    # Attach local tz and convert to UTC
    aware_local = naive_local.replace(tzinfo=tz)
    aware_utc = aware_local.astimezone(timezone.utc)
    return aware_utc

def lon_to_sign_deg(lon_deg: float) -> Dict[str, float | int | str]:
    lon_deg = lon_deg % 360.0
    sign_index = int(lon_deg // 30)
    sign = ZODIAC[sign_index]
    deg_in_sign = lon_deg - 30 * sign_index
    d = int(deg_in_sign)
    m_full = (deg_in_sign - d) * 60
    m = int(m_full)
    s = round((m_full - m) * 60, 2)
    return {"sign": sign, "deg": d, "min": m, "sec": s, "lonDeg": round(lon_deg, 6)}

def compute_geocentric_ecliptic_longitudes(dt_utc: datetime) -> List[dict]:
    t = TS.from_datetime(dt_utc)  # dt_utc must be timezone-aware UTC
    positions = []
    for name, target in PLANETS.items():
        astrometric = EARTH.at(t).observe(target)
        lon, lat, distance = astrometric.frame_latlon(ecliptic_frame)
        pos = lon_to_sign_deg(lon.degrees)
        positions.append({"planet": name, **pos})
    return positions

# ============================
# Endpoints
# ============================
@app.get("/")
def health():
    return {"status": "ok", "service": "Astrology Compute API"}

# simple in-memory store (resets on redeploy)
CHART_STORE: Dict[str, dict] = {}

@app.post("/natal-charts", response_model=CreateNatalChartResponse)
def create_natal_chart(body: CreateNatalChartRequest):
    dt_utc = to_dt(body.date, body.time, body.timezone)
    positions = compute_geocentric_ecliptic_longitudes(dt_utc)
    cid = "chart_" + uuid.uuid4().hex[:10]
    CHART_STORE[cid] = {
        "dt_utc": dt_utc.isoformat(),
        "positions": positions,
        "request": body.model_dump(),
    }
    return CreateNatalChartResponse(chartId=cid, positions=positions)

@app.post("/transits", response_model=ComputeTransitsResponse)
def compute_transits(body: ComputeTransitsRequest):
    # Validate target datetime format (we accept with/without trailing 'Z')
    try:
        _ = datetime.fromisoformat(body.targetDateTime.replace("Z", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="targetDateTime must be ISO 8601")

    # Placeholder aspect sample
    sample = [TransitAspect(
        transitingPlanet="Mars",
        natalPlanet="Venus",
        type="trine",
        orbDegrees=2.1,
        applying=True,
    )]

    return ComputeTransitsResponse(
        chartId=body.chartId,
        targetDateTime=body.targetDateTime,
        aspects=sample,
        transitingPositions=[],
    )
