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

def test_case_30():

    # Set the case properties.
    state_temperature = 290.0
    state_pressure = 1.0E+06
    state_liquid_fraction = 0.8

    # Define the initial state of the vessel.
    state = State(temperature = state_temperature, pressure = state_pressure, liquid_fraction = state_liquid_fraction)

    # Define the material.
    # METHANE+ETHANE+HYDROGEN+HYDROGEN SULFIDE
    material = Material('Case30_Material', [MaterialComponent('METHANE', 0.25), MaterialComponent('ETHANE', 0.25), MaterialComponent('HYDROGEN', 0.25), MaterialComponent('HYDROGEN SULFIDE', 0.25)], component_count = 4)

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
        if (abs((flash_calculation.flash_result.total_fluid_density-8.777167721290303)/8.777167721290303)>1e-3):
            assert False,f'Regression failed with flash_calculation.flash_result.total_fluid_density = {flash_calculation.flash_result.total_fluid_density}'
        if (flash_calculation.flash_result.fluid_phase != 1):
            assert False,f'Regression failed with flash_calculation.flash_result.fluid_phase = {flash_calculation.flash_result.fluid_phase}'
        if (abs((flash_calculation.flash_result.bubble_point_temperature-45.7498568184341)/45.7498568184341)>1e-3):
            assert False,f'Regression failed with flash_calculation.flash_result.bubble_point_temperature = {flash_calculation.flash_result.bubble_point_temperature}'
        if (abs((flash_calculation.flash_result.bubble_point_pressure-13803578.156685727)/13803578.156685727)>1e-3):
            assert False,f'Regression failed with flash_calculation.flash_result.bubble_point_pressure = {flash_calculation.flash_result.bubble_point_pressure}'
        print(f'SUCCESS: flash_calculation ({flash_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED flash_calculation with result code {resultCode}'
