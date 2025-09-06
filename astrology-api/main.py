from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Dict
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from skyfield.api import load
from skyfield.framelib import ecliptic_frame
import hashlib, pathlib

APP_VERSION = "astro-api v7"

app = FastAPI(title=f"Astrology API ({APP_VERSION})")

# -------- Health ----------
@app.get("/")
def health():
    return {"ok": True, "version": APP_VERSION}

@app.get("/ping")
def ping():
    return {"message": "pong", "version": APP_VERSION}

@app.get("/__whoami")
def whoami():
    p = pathlib.Path(__file__)
    return {"file": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "version": APP_VERSION}

# -------- Models ----------
class IncludeFlags(BaseModel):
    lots: bool = False
    nodes: bool = False
    sect: bool = False
    visibility: bool = False

class PositionsReq(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    time: str = Field(..., description="HH:MM 24h")
    timezone: str = Field(..., description='IANA "Africa/Johannesburg" or fixed "+02:00"')
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    house_system: Literal["whole_sign"]
    zodiac: Literal["tropical", "sidereal"] = "tropical"
    include: IncludeFlags = IncludeFlags()

    @field_validator("date")
    @classmethod
    def _v_date(cls, v: str) -> str:
        try: datetime.strptime(v, "%Y-%m-%d")
        except ValueError: raise ValueError("date must be YYYY-MM-DD")
        return v

    @field_validator("time")
    @classmethod
    def _v_time(cls, v: str) -> str:
        try: datetime.strptime(v, "%H:%M")
        except ValueError: raise ValueError("time must be HH:MM (24-hour)")
        return v

# -------- Time helpers ----------
def parse_tz(tz: str) -> timezone:
    if "/" in tz:
        try:
            return ZoneInfo(tz)
        except Exception:
            raise HTTPException(400, f"Unknown IANA timezone: {tz}")
    try:
        if len(tz) in (6, 9) and tz[0] in "+-" and tz[3] == ":":
            sign = 1 if tz[0] == "+" else -1
            hh = int(tz[1:3]); mm = int(tz[4:6]); ss = int(tz[7:9]) if len(tz) == 9 else 0
            return timezone(timedelta(hours=sign*hh, minutes=sign*mm, seconds=sign*ss))
        return datetime.strptime(tz, "%z").tzinfo  # type: ignore
    except Exception:
        raise HTTPException(400, f"Invalid fixed offset timezone: {tz}")

def to_utc(d: str, hhmm: str, tz: str) -> datetime:
    local = datetime.fromisoformat(f"{d}T{hhmm}:00")
    return local.replace(tzinfo=parse_tz(tz)).astimezone(timezone.utc)

# -------- Formatting ----------
SIGN_NAMES = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def split_dms(lon_deg: float):
    total = lon_deg % 360.0
    sign_i = int(total // 30)
    local = total - sign_i * 30
    d = int(local)
    m_float = (local - d) * 60
    m = int(m_float)
    s = round((m_float - m) * 60, 2)
    return sign_i, d, m, s, round(total, 6)

# -------- Skyfield (one-time) ----------
TS = load.timescale()
EPH = load("de421.bsp")
EARTH = EPH["earth"]

BODY_KEYS: Dict[str, object] = {
    "Sun": "sun",
    "Moon": "moon",
    "Mercury": "mercury",
    "Venus": "venus",
    "Mars": "mars",
    "Jupiter": ("jupiter barycenter", "jupiter"),
    "Saturn": ("saturn barycenter", "saturn"),
}

def resolve_body(key):
    if isinstance(key, tuple):
        for k in key:
            if k in EPH:
                return EPH[k]
        raise KeyError(f"No ephemeris key found for {key}")
    return EPH[key]

def geocentric_ecliptic_longitudes(t) -> Dict[str, float]:
    """Tropical ecliptic longitudes of date (0° = vernal equinox of date)."""
    longs: Dict[str, float] = {}
    for name, key in BODY_KEYS.items():
        target = resolve_body(key)
        ast = EARTH.at(t).observe(target).apparent()
        # ✅ Skyfield returns (latitude, longitude, distance)
        lat, lon, dist = ast.frame_latlon(ecliptic_frame)
        longs[name] = float(lon.degrees % 360.0)
    return longs

# -------- Route ----------
@app.post("/positions")
def positions(req: PositionsReq):
    try:
        utc_dt = to_utc(req.date, req.time, req.timezone)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Bad date/time/timezone: {e}")

    t = TS.utc(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second)

    try:
        longs = geocentric_ecliptic_longitudes(t)
    except Exception as e:
        raise HTTPException(500, f"Ephemeris error: {e}")

    out = []
    for planet in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn"]:
        lon = longs[planet]
        si, d, m, s, total = split_dms(lon)
        out.append({"planet": planet, "sign": SIGN_NAMES[si], "deg": d, "min": m, "sec": s, "lonDeg": total})

    return {
        "chartId": f"chart_{utc_dt.isoformat()}",
        "used_timestamp_utc": utc_dt.isoformat(),
        "house_system": req.house_system,
        "zodiac": req.zodiac,
        "positions": out
    }
