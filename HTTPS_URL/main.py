from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Dict
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from skyfield.api import load
from skyfield.framelib import ecliptic_frame

app = FastAPI()

# ---------- Pydantic models ----------

class IncludeFlags(BaseModel):
    lots: bool = False
    nodes: bool = False
    sect: bool = False
    visibility: bool = False

class PositionsReq(BaseModel):
    date: str = Field(..., description='YYYY-MM-DD')
    time: str = Field(..., description='HH:MM 24-hour')
    timezone: str = Field(..., description='IANA like Africa/Johannesburg or fixed offset like +02:00')
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    house_system: Literal["whole_sign"]
    zodiac: Literal["tropical", "sidereal"] = "tropical"
    include: IncludeFlags = IncludeFlags()

    @field_validator("date")
    @classmethod
    def _check_date(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("date must be YYYY-MM-DD")
        return v

    @field_validator("time")
    @classmethod
    def _check_time(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("time must be HH:MM (24-hour)")
        return v

# ---------- Helpers ----------

SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

def parse_tz(tz: str) -> timezone:
    """Return a tzinfo from IANA name or fixed offset like +02:00 / -05:30."""
    if "/" in tz:  # IANA
        try:
            return ZoneInfo(tz)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Unknown IANA timezone: {tz}")
    # fixed offset e.g. +02:00
    try:
        if len(tz) in (6, 9) and (tz[0] in "+-") and (tz[3] == ":"):
            sign = 1 if tz[0] == "+" else -1
            hh = int(tz[1:3])
            mm = int(tz[4:6])
            ss = int(tz[7:9]) if len(tz) == 9 else 0
            delta = timedelta(hours=sign*hh, minutes=sign*mm, seconds=sign*ss)
            return timezone(delta)
        # also allow "+0200"
        dt = datetime.strptime(tz, "%z")
        return dt.tzinfo  # type: ignore
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid fixed offset timezone: {tz}")

def to_utc(dt_date: str, hhmm: str, tz: str) -> datetime:
    local = datetime.fromisoformat(f"{dt_date}T{hhmm}:00")
    tzinfo = parse_tz(tz)
    return local.replace(tzinfo=tzinfo).astimezone(timezone.utc)

def dms_from_degrees(deg_float: float):
    """Return (deg, min, sec) where deg in [0..29] for sign local degrees."""
    total = deg_float % 360.0
    sign_index = int(total // 30)
    local = total - sign_index * 30
    d = int(local)
    m_float = (local - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return sign_index, d, m, s, total

# Map Skyfield body names (DE421 uses barycenters for outer planets)
BODY_KEYS = {
    "Sun": "sun",
    "Moon": "moon",
    "Mercury": "mercury",
    "Venus": "venus",
    "Mars": "mars",
    "Jupiter": ("jupiter barycenter", "jupiter"),
    "Saturn": ("saturn barycenter", "saturn"),
}

def compute_geocentric_longitudes(t) -> Dict[str, float]:
    eph = load("de421.bsp")  # ensure this is preloaded in your container
    earth = eph["earth"]
    longs = {}
    for label, key in BODY_KEYS.items():
        target = None
        if isinstance(key, tuple):
            for k in key:
                if k in eph:
                    target = eph[k]
                    break
        else:
            target = eph[key]
        if target is None:
            raise HTTPException(status_code=500, detail=f"Ephemeris missing body for {label}")

        astrometric = earth.at(t).observe(target)
        # Ecliptic of date (tropical zodiac)
        lon, lat, distance = astrometric.frame_latlon(ecliptic_frame)
        longs[label] = lon.degrees % 360.0
    return longs

# ---------- Routes ----------

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.post("/positions")
def positions(req: PositionsReq):
    # 1) Resolve timestamp
    utc_dt = to_utc(req.date, req.time, req.timezone)

    # 2) Skyfield time
    ts = load.timescale()
    t = ts.utc(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour, utc_dt.minute, utc_dt.second
    )

    # 3) Planet longitudes (geocentric, ecliptic of date)
    try:
        longs = compute_geocentric_longitudes(t)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skyfield error: {e}")

    # 4) Build response list
    positions = []
    for planet in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"]:
        lon = longs[planet]
        sign_idx, d, m, s, total = dms_from_degrees(lon)
        positions.append({
            "planet": planet,
            "sign": SIGN_NAMES[sign_idx],   # remove if you don't want sign names in API
            "deg": d,
            "min": m,
            "sec": round(s, 2),
            "lonDeg": round(total, 6)
        })

    return {
        "chartId": f"chart_{utc_dt.isoformat()}",
        "used_timestamp_utc": utc_dt.isoformat(),
        "house_system": req.house_system,
        "zodiac": req.zodiac,
        "positions": positions
    }
