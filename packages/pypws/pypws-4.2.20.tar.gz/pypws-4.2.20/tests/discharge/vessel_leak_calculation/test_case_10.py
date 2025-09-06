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

def test_case_10():

    """
    Vessel leak calculation test case with the following properties:

        material_name = 'N-BUTANE'
        state_temperature = 300.0
        state_pressure = 3.0E+05
        vessel_shape = VesselShape.VESSEL_CUBOID
        vessel_height = 2.0
        vessel_width = 1.0
        vessel_length = 3.0
        leak_hole_diameter = 0.05
        time_varying_option = TimeVaryingOption.INITIAL_RATE
        leak_hole_height_fraction = 0.2
    """

    # Set the case properties.
    material_name = 'N-BUTANE'
    state_temperature = 300.0
    state_pressure = 3.0E+05
    vessel_shape = VesselShape.VESSEL_CUBOID
    vessel_height = 2.0
    vessel_width = 1.0
    vessel_length = 3.0
    leak_hole_diameter = 0.05
    time_varying_option = TimeVaryingOption.INITIAL_RATE
    leak_hole_height_fraction = 0.2

    # Define the initial state of the vessel.
    state = State(temperature = state_temperature, pressure = state_pressure, liquid_fraction = 0.0)

    # Define the material contained by the vessel.
    material = Material(material_name, [MaterialComponent(material_name, 1.0)])

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
    # The vessel is a horizontal cylinder with a diameter of 8m and a length of 16m.
    # All other values are defaulted.
    vessel = Vessel(state = vessel_state_calculation.output_state, material = vessel_state_calculation.material, vessel_conditions = vessel_state_calculation.vessel_conditions, height = vessel_height, width = vessel_width, length = vessel_length, shape = vessel_shape, liquid_fill_fraction_by_volume = 0.5)

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
        if (abs((vessel_leak_calculation.discharge_records[0].mass_flow- 18.596151455819438)/ 18.596151455819438)>1e-3):
            assert False,f'Regression failed with vessel_leak_calculation.discharge_records[0].mass_flow = {vessel_leak_calculation.discharge_records[0].mass_flow}'
        if (len(vessel_leak_calculation.discharge_records) != 2):
            assert False,f'Regression failed with len(vessel_leak_calculation.discharge_records) = {len(vessel_leak_calculation.discharge_records)}'
        if (abs((vessel_leak_calculation.discharge_records[0].final_velocity - 82.9875939245342)/82.9875939245342)>1e-3):
            assert False,f'Regression failed with vessel_leak_calculation.discharge_records[0].final_velocity = {vessel_leak_calculation.discharge_records[0].final_velocity}'
        if (abs((vessel_leak_calculation.discharge_records[0].droplet_diameter - 0.00024867091738833337)/0.00024867091738833337)>1e-3):
            assert False,f'Regression failed with vessel_leak_calculation.discharge_records[0].droplet_diameter = {vessel_leak_calculation.discharge_records[0].droplet_diameter}'
        print(f'SUCCESS: vessel_leak_calculation ({vessel_leak_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED vessel_leak_calculation with result code {resultCode}'
