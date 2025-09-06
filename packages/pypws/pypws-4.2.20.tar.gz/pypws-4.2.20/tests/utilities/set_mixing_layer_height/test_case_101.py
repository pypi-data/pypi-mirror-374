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


from pypws.calculations import SetMixingLayerHeightCalculation
from pypws.entities import Weather
from pypws.enums import AtmosphericStabilityClass, ResultCode


def test_case_101():

    # Set the weather
    weather = Weather(wind_speed = 5.0, stability_class = AtmosphericStabilityClass.STABILITY_D)

    # Create a mixture constant properties calculation using the material.
    set_mixing_layer_height_calculation = SetMixingLayerHeightCalculation(weather)

    # Run the calculation
    print('Running set_mixing_layer_height_calculation...')
    resultCode = set_mixing_layer_height_calculation.run()

    # Print any messages.
    if len(set_mixing_layer_height_calculation.messages) > 0:
        print('Messages:')
        for message in set_mixing_layer_height_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (set_mixing_layer_height_calculation.updated_weather.mixing_layer_height != 800.0):
            assert False, f'FAILED set_mixing_layer_height_calculation with mixing layer height {set_mixing_layer_height_calculation.updated_weather.mixing_layer_height}'
        print(f'SUCCESS: set_mixing_layer_height_calculation ({set_mixing_layer_height_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED set_mixing_layer_height_calculation with result code {resultCode}'