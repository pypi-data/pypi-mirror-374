import os
import pathlib
import sys

# When running locally the environment variable PYPWS_RUN_LOCALLY needs to be set to True.
# Check if the environment variable is set
if os.getenv('PYPWS_RUN_LOCALLY') != None and os.getenv('PYPWS_RUN_LOCALLY').lower() == 'true':
    # Navigate to the PYPWS directory by searching upwards until it is found.
    current_dir = pathlib.Path(__file__).resolve()

    while current_dir.name.lower() != 'package':
        current_dir = current_dir.parent

    # Insert the path to the pypws package into sys.path.
    sys.path.insert(0, f'{current_dir}')

from pypws.calculations import FlashCalculation
from pypws.entities import Material, MaterialComponent, State
from pypws.enums import ResultCode

"""
This sample demonstrates how to use the flash calculation along with with the dependent entities.
"""

def test_case_27():

    # Set the case properties.
    state_temperature = 270.0
    state_pressure = 1.5E+05
    state_liquid_fraction = 0.7

    # Define the initial state of the vessel.
    state = State(temperature = state_temperature, pressure = state_pressure, liquid_fraction = state_liquid_fraction)

    # Define the material.
    # AMMONIA+TRIMETHYLAMINE+WATER
    material = Material('Case27_Material', [MaterialComponent('AMMONIA', 0.333), MaterialComponent('TRIMETHYLAMINE', 0.333), MaterialComponent('WATER', 0.334)], component_count = 3)

    # Create a flash calculation using the material and state.
    flash_calculation = FlashCalculation(material, state)

    # Run the flash calculation.
    print('Running flash_calculation...')
    resultCode = flash_calculation.run()

    # Print any messages.
    if len(flash_calculation.messages) > 0:
        print('Messages:')
        for message in flash_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (abs((flash_calculation.flash_result.total_fluid_density-96.46994608249469)/96.46994608249469)>1e-3):
            assert False,f'Regression failed with flash_calculation.flash_result.total_fluid_density = {flash_calculation.flash_result.total_fluid_density}'
        if (flash_calculation.flash_result.fluid_phase != 2):
            assert False,f'Regression failed with flash_calculation.flash_result.fluid_phase = {flash_calculation.flash_result.fluid_phase}'
        if (abs((flash_calculation.flash_result.bubble_point_temperature-269.42243315914885)/269.42243315914885)>1e-3):
            assert False,f'Regression failed with flash_calculation.flash_result.bubble_point_temperature = {flash_calculation.flash_result.bubble_point_temperature}'
        if (abs((flash_calculation.flash_result.bubble_point_pressure-153386.54309610242)/153386.54309610242)>1e-3):
            assert False,f'Regression failed with flash_calculation.flash_result.bubble_point_pressure = {flash_calculation.flash_result.bubble_point_pressure}'
        print(f'SUCCESS: flash_calculation ({flash_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED flash_calculation with result code {resultCode}'
