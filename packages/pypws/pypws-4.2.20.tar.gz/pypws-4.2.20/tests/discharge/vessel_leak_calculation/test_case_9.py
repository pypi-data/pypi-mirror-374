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

from pypws.calculations import VesselLeakCalculation, VesselStateCalculation
from pypws.entities import (
    DischargeParameters,
    Leak,
    LocalPosition,
    Material,
    MaterialComponent,
    State,
    Vessel,
)
from pypws.enums import ResultCode, TimeVaryingOption, VesselShape

"""
This sample demonstrates how to use the vessel leak calculation along with with the dependent entities.
"""

def test_case_9():

    """
    Vessel leak calculation test case with the following properties:

        state_temperature = 250.0
        state_pressure = 5.00E+05
        vessel_shape = VesselShape.VERTICAL_CYLINDER
        vessel_height = 3.0
        vessel_diameter = 1.5
        leak_hole_diameter = 0.1
        time_varying_option = TimeVaryingOption.TIME_VARYING_RATE
        leak_hole_height_fraction = 0.0
    """

    # Set the case properties.
    state_temperature = 250.0
    state_pressure = 5.00E+05
    vessel_shape = VesselShape.VERTICAL_CYLINDER
    vessel_height = 3.0
    vessel_diameter = 1.5
    leak_hole_diameter = 0.1
    time_varying_option = TimeVaryingOption.TIME_VARYING_RATE
    leak_hole_height_fraction = 0.0

    # Define the initial state of the vessel.
    state = State(temperature = state_temperature, pressure = state_pressure, liquid_fraction = 0.0)

    # Define the material contained by the vessel.
    material = Material('N-OCTANE+N-HEPTANE', [MaterialComponent('N-OCTANE', 0.5), MaterialComponent('N-HEPTANE', 0.5)], component_count = 2)

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

    if resultCode == ResultCode.SUCCESS:
        print(f'SUCCESS: vessel_state_calculation ({vessel_state_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED vessel_state_calculation with result code {resultCode}'

    # Create a vessel to use in the leak calculation using the previously defined entities.
    vessel = Vessel(state = vessel_state_calculation.output_state, material = vessel_state_calculation.material, vessel_conditions = vessel_state_calculation.vessel_conditions, diameter = vessel_diameter, height = vessel_height, shape = vessel_shape, liquid_fill_fraction_by_volume = 0.8)

    # Create a leak to use in the vessel leak calculation.
    # The leak has a hole of diameter of 0.05m.  The time varying option is set topytest initial rate.
    leak = Leak(hole_diameter = leak_hole_diameter, hole_height_fraction = leak_hole_height_fraction , time_varying_option = time_varying_option)

    # Create discharge parameters to use in the vessel leak calculation taking all the default values.
    discharge_parameters = DischargeParameters()

    # Create a vessel leak calculation using the vessel, leak, and discharge parameters.
    vessel_leak_calculation = VesselLeakCalculation(vessel, leak, discharge_parameters)

    # Run the vessel leak calculation.
    print('Running vessel_leak_calculation...')
    resultCode = vessel_leak_calculation.run()

    # Print any messages.
    if len(vessel_leak_calculation.messages) > 0:
        print('Messages:')
        for message in vessel_leak_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (abs((vessel_leak_calculation.discharge_records[0].mass_flow- 125.74564365679295)/ 125.74564365679295)>1e-3):
            assert False,f'Regression failed with vessel_leak_calculation.discharge_records[0].mass_flow = {vessel_leak_calculation.discharge_records[0].mass_flow}'
        if (len(vessel_leak_calculation.discharge_records) != 698):
            assert False,f'Regression failed with len(vessel_leak_calculation.discharge_records) = {len(vessel_leak_calculation.discharge_records)}'
        if (abs((vessel_leak_calculation.discharge_records[0].final_velocity - 36.48936892716285)/36.48936892716285)>1e-3):
            assert False,f'Regression failed with vessel_leak_calculation.discharge_records[0].final_velocity = {vessel_leak_calculation.discharge_records[0].final_velocity}'
        if (abs((vessel_leak_calculation.discharge_records[0].droplet_diameter - 0.0001917147651424711)/0.0001917147651424711)>1e-3):
            assert False,f'Regression failed with vessel_leak_calculation.discharge_records[0].droplet_diameter = {vessel_leak_calculation.discharge_records[0].droplet_diameter}'
        print(f'SUCCESS: vessel_leak_calculation ({vessel_leak_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED vessel_leak_calculation with result code {resultCode}'
