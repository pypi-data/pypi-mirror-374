import os
import pathlib
import sys

run_locally = os.getenv('PYPWS_RUN_LOCALLY')
if run_locally and run_locally.lower() == 'true':
    # Navigate to the PYPWS directory by searching upwards until it is found.
    current_dir = pathlib.Path(__file__).resolve()

    while current_dir.name.lower() != 'package':
        if current_dir.parent == current_dir:  # Check if the current directory is the root directory
            raise FileNotFoundError("The 'pypws' directory was not found in the path hierarchy.")
        current_dir = current_dir.parent

    # Insert the path to the pypws package into sys.path.
    sys.path.insert(0, f'{current_dir}')

from pypws.calculations import VesselStateCalculation
from pypws.entities import Material, MaterialComponent, State


def test_natural_gas_vessel_state_calculation():
    # Define the initial state of the vessel.
    state = State(temperature=136.25, pressure=5.0e5, liquid_fraction=0.8)
    # Define the material contained by the vessel.
    material = Material("NATURAL_GAS", [MaterialComponent("METHANE", 0.95), MaterialComponent("ETHANE", 0.05)], component_count = 2)

    # Create a vessel state calculation using the material and state.
    vessel_state_calculation = VesselStateCalculation(material, state)

    # Run the vessel state calculation.
    print('Running vessel_state_calculation...')
    resultCode = vessel_state_calculation.run()

    # Print any messages.
    if len(vessel_state_calculation.messages) > 0:
        print('Messages:')
        for message in vessel_state_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        if (vessel_state_calculation.vessel_conditions != 4):
            assert False,f'Regression failed with vessel_state_calculation.vessel_conditions = {vessel_state_calculation.vessel_conditions }'
        print(f'SUCCESS: vessel_state_calculation ({vessel_state_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED vessel_state_calculation with result code {resultCode}'

