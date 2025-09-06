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


from pypws.calculations import ReliefValveMinTemperatureCalculation
from pypws.entities import Material, MaterialComponent
from pypws.enums import ResultCode


def test_case_140():
    
    """
    Test for relief valve minimum temperature calculation with the following inputs

    Material = "PROPANE"
    Pressure = 1e6

    """

    # Define the material
    material = Material(
        name="PROPANE",
        components=[
            MaterialComponent(
                name="PROPANE",
                mole_fraction=1.0
            )
        ]
    )

    # Define the pressure
    pressure = 1e6

    # Create a relief valve minimum temperature calculation
    relief_valve_min_temperature_calculation = ReliefValveMinTemperatureCalculation(material = material, pressure = pressure)

    # Run the calculation
    print ('Running relief_valve_min_temperature_calculation')
    result_code = relief_valve_min_temperature_calculation.run()

    # Print any messages.
    if len(relief_valve_min_temperature_calculation.messages) > 0:
        print('Messages:')
        for message in relief_valve_min_temperature_calculation.messages:
            print(message)

    if result_code == ResultCode.SUCCESS:
        if (abs((relief_valve_min_temperature_calculation.min_temperature - 300.04391253626204)/300.04391253626204)> 1e-3):
            assert False,f'Regression failed with relief_valve_min_temperature_calculation.min_temperature = {relief_valve_min_temperature_calculation.min_temperature}'
        print(f'SUCCESS: relief_valve_min_temperature_calculation ({relief_valve_min_temperature_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED relief_valve_min_temperature_calculation with result code {result_code}'