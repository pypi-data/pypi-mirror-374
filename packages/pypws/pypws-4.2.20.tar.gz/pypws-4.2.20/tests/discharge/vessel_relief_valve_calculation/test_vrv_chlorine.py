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

def test_vrv_chlorine():

    # Define the initial state of the vessel.
    state = State(temperature=320.0, pressure=float(1e6), liquid_fraction=1.0)

    # Define the material contained by the vessel.
    material = Material("CHLORINE", [MaterialComponent("CHLORINE", 1.0)])

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

    # Create a vessel to use in the relief valve calculation using the previously defined entities. The vessel is a horizontal cylinder with a diameter of 2m and a length of 5m.
    vessel = Vessel(state=state, material=material, vessel_conditions=vessel_state_calculation.vessel_conditions, liquid_fill_fraction_by_volume=0.7, shape=VesselShape.HORIZONTAL_CYLINDER, diameter=2, length=5)

    # Create a relief valve to use in the vessel relief valve calculation. Pipe diameter is 0.02m, pipe length is 10m, and pipe height fraction is 1.
    relief_valve = ReliefValve(pipe_diameter=0.02, pipe_length=10.0, pipe_height_fraction=1, relief_valve_constriction_diameter=0.02)

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
        if (abs((vessel_relief_valve_calculation.discharge_result.release_mass -  466.32195097490285 )/ 466.32195097490285 ) > 1e-3):
            assert False, f'Regression failed with vessel_relief_valve_calculation.discharge_result.release_mass {vessel_relief_valve_calculation.discharge_result.release_mass}'
        if (len(vessel_relief_valve_calculation.discharge_records) != 2):
            assert False, f'Regression failed with len(vessel_relief_valve_calculation.discharge_records) = {len(vessel_relief_valve_calculation.discharge_records)}'
        if (abs((vessel_relief_valve_calculation.discharge_records[1].time - 1075.2115493324122) /  1075.2115493324122) > 1e-3):
            assert False,f'Regression failed with vessel_relief_valve_calculation.discharge_records[1].time = {vessel_relief_valve_calculation.discharge_records[1].time}'
        if (abs((vessel_relief_valve_calculation.discharge_records[0].mass_flow - 0.43370251302121643) /  0.43370251302121643) > 1e-3):
            assert False,f'Regression failed with vessel_relief_valve_calculation.discharge_records[0].mass_flow = {vessel_relief_valve_calculation.discharge_records[0].mass_flow}'
        if (abs((vessel_relief_valve_calculation.discharge_records[0].orifice_state.pressure - 217541.03350332877 )/  217541.03350332877) > 1e-3):
            assert False,f'Regression failed with vessel_relief_valve_calculation.discharge_records[0].orifice_state.pressure = {vessel_relief_valve_calculation.discharge_records[0].orifice_state.pressure}'
        if (abs((vessel_relief_valve_calculation.discharge_records[0].final_velocity -  276.4442859277149)/  276.4442859277149) > 1e-3):
            assert False,f'Regression failed with vessel_relief_valve_calculation.discharge_records[0].final_velocity = {vessel_relief_valve_calculation.discharge_records[0].final_velocity}'
        print(f'vessel_relief_valve_calculation.discharge_result.release_mass: {vessel_relief_valve_calculation.discharge_result.release_mass} [kg]')
        print(f'SUCCESS: vessel_relief_valve_calculation ({vessel_relief_valve_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED vessel_relief_valve_calculation with result code {resultCode}'
