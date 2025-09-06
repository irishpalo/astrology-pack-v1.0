from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from skyfield.api import load
from skyfield.framelib import ecliptic_frame

# if app isn't defined yet in this file, define it:
try:
    app
except NameError:
    app = FastAPI()

@app.get("/ping")
def ping():
    return {"message": "pong"}

class PositionsReq(BaseModel):
    date: str
    time: str
    timezone: str
    latitude: float
    longitude: float
    house_system: Literal["whole_sign"]
    zodiac: Literal["tropical","sidereal"] = "tropical"
    include: dict

def to_utc(d: str, hhmm: str, tz: str) -> datetime:
    local = datetime.fromisoformat(f"{d}T{hhmm}:00")
    tzinfo = ZoneInfo(tz) if "/" in tz else datetime.strptime(tz, "%z").tzinfo
    return local.replace(tzinfo=tzinfo).astimezone(timezone.utc)

@app.post("/positions")
def positions(req: PositionsReq):
    utc_dt = to_utc(req.date, req.time, req.timezone)
    ts = load.timescale()
    t = ts.utc(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second)

    # simple Sun example (expand later)
    eph = load("de421.bsp"); earth = eph["earth"]
    lon = earth.at(t).observe(eph["sun"]).frame_latlon(ecliptic_frame)[0].degrees % 360.0

    return {
        "chartId": f"chart_{utc_dt.isoformat()}",
        "used_timestamp_utc": utc_dt.isoformat(),
        "positions": [{"planet":"Sun","lonDeg": round(lon,6)}]
    }
