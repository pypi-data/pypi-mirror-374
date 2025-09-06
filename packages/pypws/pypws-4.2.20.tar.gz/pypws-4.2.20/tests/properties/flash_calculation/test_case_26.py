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

def test_case_26():

    # Set the case properties.
    state_temperature = 270.0
    state_pressure = 8.0E+06
    state_liquid_fraction = 0.8
        
    # Define the initial state of the vessel.
    state = State(temperature = state_temperature, pressure = state_pressure, liquid_fraction = state_liquid_fraction)

    # Define the material.
    # METHANE+ETHANE+PROPANE+N-BUTANE+N-PENTANE
    material = Material('Case26_Material', [MaterialComponent('METHANE', 0.2), MaterialComponent('ETHANE', 0.2), MaterialComponent('PROPANE', 0.2), MaterialComponent('N-BUTANE', 0.2), MaterialComponent('N-PENTANE', 0.2)], component_count = 5)

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
        if (abs((flash_calculation.flash_result.total_fluid_density-483.1833445460695)/483.1833445460695)>1e-3):
            assert False,f'Regression failed with flash_calculation.flash_result.total_fluid_density = {flash_calculation.flash_result.total_fluid_density}'
        if (flash_calculation.flash_result.fluid_phase != 3):
            assert False,f'Regression failed with flash_calculation.flash_result.fluid_phase = {flash_calculation.flash_result.fluid_phase}'
        if (abs((flash_calculation.flash_result.bubble_point_temperature-319.5331124566492)/319.5331124566492)>1e-3):
            assert False,f'Regression failed with flash_calculation.flash_result.bubble_point_temperature = {flash_calculation.flash_result.bubble_point_temperature}'
        if (abs((flash_calculation.flash_result.bubble_point_pressure-4479259.631949412)/4479259.631949412)>1e-3):
            assert False,f'Regression failed with flash_calculation.flash_result.bubble_point_pressure = {flash_calculation.flash_result.bubble_point_pressure}'
        print(f'SUCCESS: flash_calculation ({flash_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED flash_calculation with result code {resultCode}'
