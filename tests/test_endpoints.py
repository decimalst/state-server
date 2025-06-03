# tests/test_endpoints.py

import pytest
from fastapi.testclient import TestClient

from state_server.app import app, find_states_containing

client = TestClient(app)

def test_get_endpoint_valid_point():
    # right on Border of Philly: expects ["New Jersey"]
    response = client.get("/", params={"latitude": 40.0, "longitude": -75.0})
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, list)
    assert "New Jersey" in payload

def test_post_endpoint_valid_point():
    # Nevada: expects ["Nevada"]
    response = client.post("/", data={"latitude": 39.0, "longitude": -116.0})
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, list)
    assert "Nevada" in payload

@pytest.mark.parametrize(
    "payload, expected_status",
    [
        # out-of-bounds latitude
        ({"latitude": 100.0, "longitude": 0.0}, 422),
        # out-of-bounds longitude
        ({"latitude": 0.0, "longitude": 200.0}, 422),
        # missing fields → should be a 422 because latitude/longitude are required
        ({}, 422),
    ],
)
def test_post_endpoint_invalid(payload, expected_status):
    response = client.post("/", data=payload)
    assert response.status_code == expected_status

@pytest.mark.parametrize(
    "params, expected_status",
    [
        ({"latitude": 100.0, "longitude": 0.0}, 422),  # lat out of range
        ({"latitude": 0.0, "longitude": 200.0}, 422),  # lon out of range
        ({}, 422),  # missing params
    ],
)
def test_get_endpoint_invalid(params, expected_status):
    response = client.get("/", params=params)
    assert response.status_code == expected_status

def test_get_and_post_consistency():
    # Pick a random point, e.g. (45.0, -93.0) → Minnesota
    lat, lon = 45.0, -93.0
    # call GET
    get_resp = client.get("/", params={"latitude": lat, "longitude": lon})
    post_resp = client.post("/", data={"latitude": lat, "longitude": lon})

    assert get_resp.status_code == 200
    assert post_resp.status_code == 200

    # Both responses should give the same JSON payload
    assert sorted(get_resp.json()) == sorted(post_resp.json())
