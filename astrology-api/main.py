from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from skyfield.api import load
from skyfield.framelib import ecliptic_frame
import hashlib, pathlib

APP_VERSION = "positions-minimal v1"

app = FastAPI(title=f"Astrology API ({APP_VERSION})")

# Fingerprint: returns the path+hash of THIS file so we know what is running
@app.get("/__whoami")
def whoami():
    p = pathlib.Path(__file__)
    src = p.read_bytes()
    return {"file": str(p), "sha256": hashlib.sha256(src).hexdigest(), "version": APP_VERSION}

@app.get("/")
def health():
    return {"ok": True, "version": APP_VERSION}

@app.get("/ping")
def ping():
    return {"message": "pong", "version": APP_VERSION}

class PositionsReq(BaseModel):
    date: str           # "YYYY-MM-DD"
    time: str           # "HH:MM"
    timezone: str       # "Africa/Johannesburg" or "+02:00"
    latitude: float
    longitude: float
    house_system: Literal["whole_sign"]
    zodiac: Literal["tropical","sidereal"] = "tropical"
    include: dict

def to_utc(d: str, hhmm: str, tz: str) -> datetime:
    local = datetime.fromisoformat(f"{d}T{hhmm}:00")
    tzinfo = ZoneInfo(tz) if "/" in tz else datetime.strptime(tz, "%z").tzinfo  # type: ignore
    return local.replace(tzinfo=tzinfo).astimezone(timezone.utc)

@app.post("/positions")
def positions(req: PositionsReq):
    utc_dt = to_utc(req.date, req.time, req.timezone)
    ts = load.timescale()
    t = ts.utc(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second)

    # Sun-only demo so we can see the route is live
    eph = load("de421.bsp"); earth = eph["earth"]
    lon = earth.at(t).observe(eph["sun"]).frame_latlon(ecliptic_frame)[0].degrees % 360.0

    return {
        "chartId": f"chart_{utc_dt.isoformat()}",
        "used_timestamp_utc": utc_dt.isoformat(),
        "positions": [{"planet":"Sun","lonDeg": round(lon,6)}]
    }
