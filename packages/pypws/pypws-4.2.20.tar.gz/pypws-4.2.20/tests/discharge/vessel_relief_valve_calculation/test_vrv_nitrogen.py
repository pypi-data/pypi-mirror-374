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

from pypws.calculations import VesselReliefValveCalculation, VesselStateCalculation
from pypws.entities import (
    DischargeParameters,
    LocalPosition,
    Material,
    MaterialComponent,
    ReliefValve,
    State,
    TimeVaryingOption,
    Vessel,
    VesselConditions,
    VesselShape,
)
from pypws.enums import ResultCode

"""
This sample demonstrates how to use the vessel relief valve calculation along with with the dependent entities.
"""

def test_vrv_nitrogen():

    # Define the initial state of the vessel.
    state = State(temperature=300.0, pressure=float(4e6), liquid_fraction=1.0)

    # Define the material contained by the vessel.
    material = Material("NITROGEN", [MaterialComponent("NITROGEN", 1.0)])

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
        
    # Create a vessel to use in the relief valve calculation using the previously defined entities. The vessel is a horizontal cylinder with a diameter of 1.5m and a height of 3m.
    vessel = Vessel(state=state, material=material, vessel_conditions=vessel_state_calculation.vessel_conditions, liquid_fill_fraction_by_volume=0.7, shape=VesselShape.HORIZONTAL_CYLINDER, diameter=1.5, height=3)

    # Create a relief valve to use in the relief valve calculation. Pipe diameter is 0.5m, pipe length is 10m, and pipe height fraction is 1.
    relief_valve = ReliefValve(pipe_diameter=0.5, pipe_length=10.0, pipe_height_fraction=1, relief_valve_constriction_diameter=0.5)

    # Create a vessel relief valve calculation using the vessel, relief valve, and discharge parameters.
    vessel_relief_valve_calculation = VesselReliefValveCalculation(vessel, relief_valve, DischargeParameters())

    # Run a vessel relief valve calculation.
    print('Running vessel_relief_valve_calculation...')
    resultCode = vessel_relief_valve_calculation.run()

    assert resultCode == ResultCode.SUCCESS

    # Print any messages.
    if len(vessel_relief_valve_calculation.messages) > 0:
        print('Messages:')
        for message in vessel_relief_valve_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (abs((vessel_relief_valve_calculation.discharge_result.release_mass -   314.94879020959837)/  314.94879020959837) > 1e-3):
            assert False, f'Regression failed with vessel_relief_valve_calculation.discharge_result.release_mass {vessel_relief_valve_calculation.discharge_result.release_mass}'
        if (len(vessel_relief_valve_calculation.discharge_records) != 2):
            assert False, f'Regression failed with len(vessel_relief_valve_calculation.discharge_records) = {len(vessel_relief_valve_calculation.discharge_records)}'
        if (abs((vessel_relief_valve_calculation.discharge_records[1].time - 0.20034090677203503) / 0.20034090677203503) > 1e-3):
            assert False,f'Regression failed with vessel_relief_valve_calculation.discharge_records[1].time = {vessel_relief_valve_calculation.discharge_records[1].time}'
        if (abs((vessel_relief_valve_calculation.discharge_records[0].mass_flow -  1572.064314194075) / 1572.064314194075) > 1e-3):
            assert False,f'Regression failed with vessel_relief_valve_calculation.discharge_records[0].mass_flow = {vessel_relief_valve_calculation.discharge_records[0].mass_flow}'
        if (abs((vessel_relief_valve_calculation.discharge_records[0].orifice_state.pressure -  2165508.2851427207)/   2165508.2851427207) > 1e-3):
            assert False,f'Regression failed with vessel_relief_valve_calculation.discharge_records[0].orifice_state.pressure = {vessel_relief_valve_calculation.discharge_records[0].orifice_state.pressure}'
        if (abs((vessel_relief_valve_calculation.discharge_records[0].final_velocity -554.7205461435867)/ 554.7205461435867) > 1e-3):
            assert False,f'Regression failed with vessel_relief_valve_calculation.discharge_records[0].final_velocity = {vessel_relief_valve_calculation.discharge_records[0].final_velocity}'
        print(f'vessel_relief_valve_calculation.discharge_result.release_mass: {vessel_relief_valve_calculation.discharge_result.release_mass} [kg]')
        print(f'SUCCESS: vessel_relief_valve_calculation ({vessel_relief_valve_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED vessel_relief_valve_calculation with result code {resultCode}'
