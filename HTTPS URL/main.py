from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import math
import numpy as np
from skyfield.api import load, wgs84, Star
from skyfield.framelib import ecliptic_frame

# =========================
# App
# =========================
app = FastAPI(title="Astrology Compute API — Full Chart")

# =========================
# Models
# =========================
class IncludeFlags(BaseModel):
    lots: bool = True
    nodes: bool = True
    sect: bool = False     # reserved
    visibility: bool = False  # reserved
    lots_in_aspects: bool = False  # include Lots in the aspect matrix

class CreateNatalChartRequest(BaseModel):
    date: str                          # "YYYY-MM-DD"
    time: str                          # "HH:MM" or "HH:MM:SS"
    timezone: str                      # IANA tz, e.g. "Africa/Johannesburg"
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    elevation_m: float = 0.0
    house_system: Optional[str] = "whole_sign"
    zodiac: Optional[str] = "tropical"
    include: Optional[IncludeFlags] = IncludeFlags()

class CreateNatalChartResponse(BaseModel):
    chartId: str
    utc: str
    positions: List[Dict]
    ascendant: Dict
    mc: Dict
    houses: List[Dict]
    lots: Optional[Dict] = None
    aspects: List[Dict]

# =========================
# Constants & Ephemeris
# =========================
PLANETS = [
    ("Sun", "sun"),
    ("Moon", "moon"),
    ("Mercury", "mercury"),
    ("Venus", "venus"),
    ("Mars", "mars"),
    ("Jupiter", "jupiter barycenter"),
    ("Saturn", "saturn barycenter"),
    ("Uranus", "uranus barycenter"),
    ("Neptune", "neptune barycenter"),
    ("Pluto", "pluto barycenter"),
]
ASPECT_DEGREES = {"conjunction": 0, "sextile": 60, "square": 90, "trine": 120, "opposition": 180}
ZODIAC = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

TS = load.timescale()
EPH = load("de421.bsp")           # 1900–2050
EARTH = EPH["earth"]

# =========================
# Utilities
# =========================
def wrap360(x: float) -> float:
    return x % 360.0

def wrap180(x: float) -> float:
    return ((x + 180.0) % 360.0) - 180.0

def dms(x: float) -> Tuple[int,int,float]:
    d = int(math.floor(x))
    m_float = (x - d) * 60.0
    m = int(math.floor(m_float))
    s = (m_float - m) * 60.0
    return d, m, s

def to_sign_tuple(lon_deg: float) -> Tuple[str,int,int,float]:
    lon = wrap360(lon_deg)
    sign = ZODIAC[int(lon // 30)]
    within = lon - 30*int(lon//30)
    return (sign, *dms(within))

def parse_local_to_utc(date_str: str, time_str: str, tz: str) -> datetime:
    tpart = time_str.strip()
    if len(tpart.split(":")) == 2:
        tpart += ":00"
    try:
        local = datetime.fromisoformat(f"{date_str}T{tpart}")
    except ValueError:
        raise HTTPException(status_code=400, detail="Time must be HH:MM or HH:MM:SS")
    try:
        aware_local = local.replace(tzinfo=ZoneInfo(tz))
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {tz}")
    return aware_local.astimezone(timezone.utc)

# ---------- Ecliptic <-> Equatorial (β=0) ----------
# For ecliptic latitude β=0, using obliquity ε:
# α = atan2( sin λ cos ε, cos λ ); δ = arcsin( sin λ sin ε )
def ra_dec_from_ecliptic_lon(lambda_deg: float, eps_deg: float) -> Tuple[float, float]:
    lam = math.radians(wrap360(lambda_deg))
    eps = math.radians(eps_deg)
    y = math.sin(lam) * math.cos(eps)
    x = math.cos(lam)
    alpha = math.degrees(math.atan2(y, x)) % 360.0
    delta = math.degrees(math.asin(math.sin(lam) * math.sin(eps)))
    return alpha, delta

# Greenwich Apparent Sidereal Time (deg) and Local Sidereal Time (deg, east long positive)
def lst_degrees(t, longitude_deg: float) -> float:
    gast_deg = (t.gast * 15.0) % 360.0
    return wrap360(gast_deg + longitude_deg)

def obliquity_deg(t) -> float:
    # Skyfield's ecliptic_frame uses true obliquity; we fetch it via Earth tilt approximation
    # Using IAU 2006 expression would be overkill; 23.4392911° is fine here; but we can take from frame:
    # For consistency, use standard mean obliquity (close to apparent); differences are arcseconds.
    return 23.439291111  # degrees

# ---------- Ascendant / MC ----------
def mc_longitude_deg(t, longitude_deg: float, eps_deg: float) -> float:
    """Solve α(λ) = LST (mod 360) for ecliptic longitude λ (β=0)."""
    lst = lst_degrees(t, longitude_deg)
    def f(lam_deg):
        alpha, _ = ra_dec_from_ecliptic_lon(lam_deg, eps_deg)
        return wrap180(alpha - lst)
    # Scan to bracket root
    xs = np.linspace(0.0, 360.0, 721)  # every 0.5°
    vals = [f(x) for x in xs]
    for i in range(len(xs)-1):
        if vals[i] == 0.0 or vals[i+1] == 0.0 or vals[i]*vals[i+1] < 0:
            a, b = xs[i], xs[i+1]
            # Bisection
            for _ in range(40):
                m = (a+b)/2
                if f(a)*f(m) <= 0:
                    b = m
                else:
                    a = m
            return wrap360((a+b)/2)
    # Fallback
    return wrap360(lst)

def asc_longitude_deg(t, latitude_deg: float, longitude_deg: float, eps_deg: float) -> float:
    """
    Find ecliptic longitude where the ecliptic intersects the local horizon to the East (Ascendant).
    We solve for λ with altitude≈0 and azimuth≈90° using numeric search.
    """
    observer = wgs84.latlon(latitude_deg, longitude_deg)

    def alt_az_for_lambda(lam_deg: float) -> Tuple[float,float]:
        ra_deg, dec_deg = ra_dec_from_ecliptic_lon(lam_deg, eps_deg)
        star = Star(ra_hours=ra_deg/15.0, dec_degrees=dec_deg)
        app = observer.at(t).observe(star).apparent()
        alt, az, _ = app.altaz()
        return alt.degrees, az.degrees

    # Find intervals where altitude crosses 0 with az near east (80°..100°)
    grid = np.linspace(0.0, 360.0, 721)  # 0.5°
    alts = []
    azs = []
    for g in grid:
        a, z = alt_az_for_lambda(g)
        alts.append(a); azs.append(z)
    for i in range(len(grid)-1):
        if alts[i] == 0.0 or alts[i+1] == 0.0 or (alts[i] < 0 and alts[i+1] > 0) or (alts[i] > 0 and alts[i+1] < 0):
            # candidate; refine if az near east
            if 80.0 <= ((azs[i]+azs[i+1])/2.0) <= 100.0:
                a, b = grid[i], grid[i+1]
                for _ in range(40):
                    m = (a+b)/2.0
                    am, zm = alt_az_for_lambda(m)
                    if (alts[i] < 0 and am > 0) or (alts[i] > 0 and am < 0):
                        b = m
                    else:
                        a = m
                return wrap360((a+b)/2.0)
    # Fallback: take best eastmost
    best_idx = np.argmin([abs(az-90.0) + abs(alt) for alt,az in zip(alts,azs)])
    return wrap360(grid[best_idx])

# ---------- Positions ----------
def apparent_ecliptic(observer, target, t) -> Tuple[float,float,float,float,float]:
    """
    Apparent geocentric ecliptic: (lon_deg, lat_deg, declination_deg, speed_deg_per_day, distance_AU)
    Speed computed via ±30 minutes.
    """
    app = observer.at(t).observe(target).apparent()
    lon, lat, _ = app.frame_latlon(ecliptic_frame)
    ra, dec, _ = app.radec()

    lon0 = lon.degrees % 360.0
    lat0 = lat.degrees
    dec0 = dec.degrees
    dist = app.distance().au

    # numeric speed dλ/dt with ±30 min
    dt_day = 30.0/(24.0*60.0)
    t_m = TS.tt_jd(t.tt - dt_day)
    t_p = TS.tt_jd(t.tt + dt_day)
    lon_m = observer.at(t_m).observe(target).apparent().frame_latlon(ecliptic_frame)[0].degrees
    lon_p = observer.at(t_p).observe(target).apparent().frame_latlon(ecliptic_frame)[0].degrees
    speed = wrap180(lon_p - lon_m) / (2*dt_day)

    return lon0, lat0, dec0, speed, dist

# ---------- Nodes & Lots ----------
def true_node_longitude(t) -> float:
    """Meeus-like series (deg)."""
    T = (t.tt - 2451545.0) / 36525.0
    mean = 125.04455501 - 1934.13618508*T + 0.0020762*(T**2) + (T**3)/467410.0 - (T**4)/60616000.0
    mean = wrap360(mean)

    D = wrap360(297.85036 + 445267.111480*T - 0.0019142*(T**2) + (T**3)/189474.0)
    M = wrap360(357.52772 + 35999.050340*T - 0.0001603*(T**2) - (T**3)/300000.0)
    Mm= wrap360(134.96298 + 477198.867398*T + 0.0086972*(T**2) + (T**3)/56250.0)
    F = wrap360(93.27191 + 483202.017538*T - 0.0036825*(T**2) + (T**3)/327270.0)

    corr = (-1.4979*math.sin(math.radians(2*D))
            + 0.1500*math.sin(math.radians(M))
            - 0.2446*math.sin(math.radians(2*F))
            - 0.1226*math.sin(math.radians(2*D + M))
            + 0.0020*math.sin(math.radians(2*D - M))
            + 0.0020*math.sin(math.radians(2*D + Mm))
            + 0.0020*math.sin(math.radians(2*D - Mm)))
    return wrap360(mean + corr/60.0)

def lots_valens(asc: float, sun: float, moon: float, venus: float, is_day: bool) -> Dict[str, float]:
    """Valens (day/night) longitudes (deg)."""
    n = lambda x: wrap360(x)
    if is_day:
        fortune = n(asc + moon - sun)
        spirit  = n(asc + sun  - moon)
        eros    = n(asc + venus - sun)
    else:
        fortune = n(asc + sun  - moon)
        spirit  = n(asc + moon - sun)
        eros    = n(asc + sun  - venus)
    return {"Fortune": fortune, "Spirit": spirit, "Eros": eros}

# ---------- Houses ----------
def whole_sign_houses_from_asc(asc_lon: float) -> List[Dict]:
    start_sign_idx = int(wrap360(asc_lon) // 30)
    houses = []
    for i in range(12):
        idx = (start_sign_idx + i) % 12
        houses.append({"house": i+1, "sign": ZODIAC[idx], "start": idx*30.0})
    return houses

# ---------- Aspects ----------
def compute_aspects(lon_map: Dict[str,float], orb: float=6.0) -> List[Dict]:
    names = list(lon_map.keys())
    out: List[Dict] = []
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            a, b = names[i], names[j]
            da, db = lon_map[a], lon_map[b]
            diff = abs(wrap180(db - da))
            for name, ang in ASPECT_DEGREES.items():
                delta = abs(diff - ang)
                if delta <= orb:
                    out.append({"a": a, "b": b, "type": name, "orbDegrees": round(delta,3)})
    return out

# =========================
# API
# =========================
@app.get("/")
def health():
    return {"status": "ok", "service": "Astrology Compute API — Full Chart"}

@app.post("/natal-charts", response_model=CreateNatalChartResponse)
def create_natal_chart(body: CreateNatalChartRequest):
    # 1) Parse local -> UTC -> Skyfield time
    dt_utc = parse_local_to_utc(body.date, body.time, body.timezone)
    t = TS.from_datetime(dt_utc)

    # 2) Basic quantities
    eps = obliquity_deg(t)
    topo = wgs84.latlon(body.latitude, body.longitude, elevation_m=body.elevation_m)

    # 3) Day/night (Sun altitude)
    sun_alt = topo.at(t).observe(EPH["sun"]).apparent().altaz()[0].degrees
    is_day = sun_alt > 0.0

    # 4) Ascendant & MC (degrees)
    asc_lon = asc_longitude_deg(t, body.latitude, body.longitude, eps)
    mc_lon  = mc_longitude_deg(t, body.longitude, eps)

    asc_sign, asc_d, asc_m, asc_s = to_sign_tuple(asc_lon)
    mc_sign,  mc_d,  mc_m,  mc_s  = to_sign_tuple(mc_lon)

    # 5) Planetary positions (apparent geocentric ecliptic)
    positions: List[Dict] = []
    longitudes: Dict[str,float] = {}
    for label, key in PLANETS:
        lon, lat, dec, speed, dist = apparent_ecliptic(EARTH, EPH[key], t)
        s, d, m, ssec = to_sign_tuple(lon)
        positions.append({
            "planet": label,
            "sign": s, "deg": d, "min": m, "sec": round(ssec,2),
            "lonDeg": round(wrap360(lon), 6),
            "latDeg": round(lat, 6),
            "declinationDeg": round(dec, 6),
            "speedDegPerDay": round(speed, 6)
        })
        longitudes[label] = wrap360(lon)

    # 6) True Node
    if body.include.nodes:
        node_lon = true_node_longitude(t)
        s, d, m, ssec = to_sign_tuple(node_lon)
        positions.append({
            "planet": "True Node",
            "sign": s, "deg": d, "min": m, "sec": round(ssec,2),
            "lonDeg": round(node_lon,6),
            "latDeg": 0.0,
            "declinationDeg": None,
            "speedDegPerDay": None
        })
        longitudes["True Node"] = node_lon

    # 7) Houses (whole sign) from Asc sign
    houses = whole_sign_houses_from_asc(asc_lon)

    # 8) Lots (Valens)
    lots_payload = None
    if body.include.lots:
        lots_vals = lots_valens(
            asc=asc_lon,
            sun=longitudes["Sun"],
            moon=longitudes["Moon"],
            venus=longitudes["Venus"],
            is_day=is_day
        )
        lots_payload = {}
        for name, lon in lots_vals.items():
            s, d, m, ssec = to_sign_tuple(lon)
            lots_payload[name] = {
                "sign": s, "deg": d, "min": m, "sec": round(ssec,2),
                "lonDeg": round(lon,6)
            }
            if body.include.lots_in_aspects:
                longitudes[name] = lon

    # 9) Aspects (Sun..Pluto + True Node [+ Lots if enabled])
    aspects = compute_aspects(longitudes, orb=6.0)

    chart_id = f"chart_{dt_utc.strftime('%Y%m%d%H%M%S')}"
    return CreateNatalChartResponse(
        chartId=chart_id,
        utc=dt_utc.isoformat(),
        positions=positions,
        ascendant={
            "sign": asc_sign, "deg": asc_d, "min": asc_m, "sec": round(asc_s,2),
            "lonDeg": round(asc_lon,6)
        },
        mc={
            "sign": mc_sign, "deg": mc_d, "min": mc_m, "sec": round(mc_s,2),
            "lonDeg": round(mc_lon,6)
        },
        houses=houses,
        lots=lots_payload,
        aspects=aspects
    )