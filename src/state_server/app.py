# state_server.py

import json
import os
from typing import List
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException
from pydantic import constr
from shapely.geometry import shape, Point

app = FastAPI(
    title="State Server",
    description="Given latitude/longitude, return which U.S. state(s) contain that point.",
    version="1.0.0",
)

# ===== 1) Load and preprocess the GeoJSON on startup =====
BASE_DIR = Path(__file__).resolve().parents[2]
GEOJSON_PATH = BASE_DIR / "files" / "us-states.json"

if not GEOJSON_PATH.exists():
    raise FileNotFoundError(
        f"Could not find '{GEOJSON_PATH}'.\n"
        "Please download a US-states GeoJSON (e.g. from:\n"
        "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json\n"
        "and save it as 'files/us-states.json' next to this repo."
    )

with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    us_states_geo = json.load(f)

# Pre-build a list of (Shapely polygon, state_name) tuples:
_STATE_POLYGONS: List[tuple] = []
for feature in us_states_geo["features"]:
    geom = shape(feature["geometry"])
    name = feature["properties"].get("name") or feature["properties"].get("NAME")  # depending on how the GeoJSON is structured
    if not isinstance(name, str):
        continue
    _STATE_POLYGONS.append((geom, name))


# ===== 2) Utility function for point-in-polygons =====

def find_states_containing(lat: float, lon: float) -> List[str]:
    """
    Return a list of all state names whose polygon contains the given (lat, lon).
    If none match, return an empty list.
    """
    pt = Point(lon, lat)  # Shapely expects (x=lon, y=lat)
    hits: List[str] = []
    for poly, name in _STATE_POLYGONS:
        if poly.contains(pt):
            hits.append(name)
    return hits


# ===== 3) Define FastAPI endpoint(s) =====

@app.post(
    "/",
    summary="Find State by Latitude/Longitude (form‐encoded)",
    response_model=List[constr(strip_whitespace=True)],  # returns a list of state names
)
async def which_state_form(
    latitude: float = Form(..., description="Latitude in decimal degrees"),
    longitude: float = Form(..., description="Longitude in decimal degrees"),
):
    """
    Accepts form‐encoded `latitude` and `longitude` (e.g. via `curl -d "latitude=40.5&longitude=-75.2" http://localhost:8080/`).
    Returns a JSON array of state name(s) that contain that point.
    """
    # Basic sanity check on lat/lon ranges
    if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
        raise HTTPException(status_code=422, detail="latitude or longitude out of bounds")

    matched = find_states_containing(latitude, longitude)
    return matched  # FastAPI will JSON-ify this


@app.get(
    "/",
    summary="Find State by Latitude/Longitude (query params)",
    response_model=List[constr(strip_whitespace=True)],
)
async def which_state_query(
    latitude: float,
    longitude: float,
):
    """
    Same behavior as POST "/", but accepts ?latitude=...&longitude=... in the URL.
    E.g.: GET /?latitude=40.5&longitude=-75.2
    """
    if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
        raise HTTPException(status_code=422, detail="latitude or longitude out of bounds")

    matched = find_states_containing(latitude, longitude)
    return matched
