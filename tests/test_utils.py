
import pytest
from state_server.app import find_states_containing

@pytest.mark.parametrize(
    "lat, lon, expected_states",
    [
        # Harrisburg, PA ( Inside Pennsylvania)
        (40.2732, -76.8867, ["Pennsylvania"]),
        # Somewhere in Nevada (approx. latitude 39, longitude -116)
        (39.0, -116.0, ["Nevada"]),
        # A point in the Atlantic (no US state)
        (0.0, 0.0, []),
    ],
)
def test_find_states_basic(lat, lon, expected_states):
    result = find_states_containing(lat, lon)
    # Sort both lists before comparing, because order of polygons isn’t guaranteed
    assert sorted(result) == sorted(expected_states)
