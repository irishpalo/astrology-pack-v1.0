from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo  # Python 3.9+
from math import modf
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
def parse_local_to_utc(date_str: str, time_str: str, tz_name: str) -> datetime:
    """Parse local date/time with an IANA tz and return an aware UTC datetime."""
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
    aware_local = naive_local.replace(tzinfo=tz)
    return aware_local.astimezone(timezone.utc)

def utc_datetime_to_ts(dt_utc: datetime):
    """Build Skyfield Time using explicit UTC components (avoids any ambiguity)."""
    # Ensure UTC & integer seconds
    dt_utc = dt_utc.astimezone(timezone.utc)
    # seconds can have fractions; preserve them
    sec_float = dt_utc.second + dt_utc.microsecond / 1_000_000
    return TS.utc(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour, dt_utc.minute, sec_float)

def lon_to_sign_deg(lon_deg: float) -> Dict[str, float | int | str]:
    # Normalize to [0, 360)
    lon_deg = lon_deg % 360.0
    sign_index = int(lon_deg // 30)
    sign = ZODIAC[sign_index]
    deg_in_sign = lon_deg - 30 * sign_index
    d = int(deg_in_sign)
    m_full = (deg_in_sign - d) * 60
    m = int(m_full)
    s = round((m_full - m) * 60, 2)
    return {"sign": sign, "deg": d, "min": m, "sec": s, "lonDeg": round(lon_deg, 6)}

def compute_geocentric_ecliptic_longitudes(t) -> List[dict]:
    """Compute apparent geocentric ecliptic longitudes for the traditional planets."""
    positions = []
    for name, target in PLANETS.items():
        # Apparent position (light-time & aberration corrections)
        astrometric = EARTH.at(t).observe(target).apparent()
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

CHART_STORE: Dict[str, dict] = {}

@app.post("/natal-charts", response_model=CreateNatalChartResponse)
def create_natal_chart(body: CreateNatalChartRequest):
    # Convert provided local time to UTC, then to Skyfield Time
    dt_utc = parse_local_to_utc(body.date, body.time, body.timezone)
    t = utc_datetime_to_ts(dt_utc)

    # Compute apparent ecliptic longitudes (location not used here; parallax negligible except Moon)
    positions = compute_geocentric_ecliptic_longitudes(t)

    cid = "chart_" + uuid.uuid4().hex[:10]
    CHART_STORE[cid] = {
        "dt_utc": dt_utc.isoformat(),
        "positions": positions,
        "request": body.model_dump(),
    }
    return CreateNatalChartResponse(chartId=cid, positions=positions)

@app.post("/transits", response_model=ComputeTransitsResponse)
def compute_transits(body: ComputeTransitsRequest):
    # Validate target datetime (accept with/without trailing Z)
    try:
        _ = datetime.fromisoformat(body.targetDateTime.replace("Z", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="targetDateTime must be ISO 8601")

    # Placeholder aspect until you want real aspect logic
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
