import os
import pathlib
import sys

# When running locally the environment variable PYPWS_RUN_LOCALLY needs to be set to True.
# Check if the environment variable is set
PYPWS_RUN_LOCALLY = os.getenv('PYPWS_RUN_LOCALLY')
if PYPWS_RUN_LOCALLY and PYPWS_RUN_LOCALLY.lower() == 'true':
    # Navigate to the PYPWS directory by searching upwards until it is found.
    current_dir = pathlib.Path(__file__).resolve()

    while current_dir.name.lower() != 'package':
        if current_dir.parent == current_dir:  # Check if the current directory is the root directory
            raise FileNotFoundError("The 'pypws' directory was not found in the path hierarchy.")
        current_dir = current_dir.parent

    # Insert the path to the pypws package into sys.path.
    sys.path.insert(0, f'{current_dir}')

from pypws.entities import LocalPosition, Material, State, Vessel

"""
Instantiate a Vessel entity with the following attributes:
- state: State entity with the following attributes:
    - temperature: 265.0
    - pressure: '5.0E5
    - liquid_fraction: 0.0
- material: Material entity with the following attributes:
    - name: 'AMMONIA'
    - components: [{'name': 'AMMONIA', 'fraction': 1.0}]
- position: LocalPosition entity with the following attributes:
    - x: 10.0
    - y: 20.0
    - z: 30.0
"""

def test_vessel():
    state = State(temperature=265.0, pressure='5.0E5', liquid_fraction=0.0)
    material = Material(name='AMMONIA', components=[{'name': 'AMMONIA', 'fraction': 1.0}])

    vessel = Vessel(state, material, location = LocalPosition(x=10.0, y=20.0, z=30.0), liquid_fill_fraction_by_volume=0.5)

    assert vessel.material.name == 'AMMONIA'
    assert vessel.state.temperature == 265.0
    assert vessel.state.pressure == '5.0E5'
    assert vessel.state.liquid_fraction == 0.0
    assert len(vessel.material.components) == 1