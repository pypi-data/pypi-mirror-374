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

from pypws.calculations import VesselLineRuptureCalculation, VesselStateCalculation
from pypws.entities import (
    DischargeParameters,
    LineRupture,
    LocalPosition,
    Material,
    MaterialComponent,
    State,
    TimeVaryingOption,
    Vessel,
    VesselConditions,
    VesselShape,
)
from pypws.enums import ResultCode

"""
This sample demonstrates how to use the vessel line rupture calculation along with with the dependent entities.
"""

def test_vlr_n_decane():

    # Define the initial state of the vessel.
    state = State(temperature=280.0, pressure=float(1.5e5), liquid_fraction=1.0)

    # Define the material contained by the vessel.
    material = Material("N-DECANE", [MaterialComponent("N-DECANE", 1.0)])

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

    # Create a vessel to use in the line rupture calculation using the previously defined entities. The vessel is a vertical cylinder with a height of 3m and a diameter of 1.5m.
    vessel = Vessel(state=state, material=material, vessel_conditions=vessel_state_calculation.vessel_conditions, liquid_fill_fraction_by_volume=0.7, shape=VesselShape.VERTICAL_CYLINDER, height=3, diameter=1.5)

    # Create a line rupture to use in the vessel line rupture calculation.Pipe diameter is 0.02m, pipe length is 10m, and pipe height fraction is 0.
    line_rupture = LineRupture(pipe_diameter=0.02, pipe_length=10.0, pipe_height_fraction=0)

    # Create a vessel line rupture calculation using the vessel, line rupture, and discharge parameters.
    vessel_line_rupture_calculation = VesselLineRuptureCalculation(vessel, line_rupture, DischargeParameters())

    # Run a vessel line rupture calculation.
    print('Running vessel_line_rupture_calculation...')
    resultCode = vessel_line_rupture_calculation.run()

    assert resultCode == ResultCode.SUCCESS

    # Print any messages.
    if len(vessel_line_rupture_calculation.messages) > 0:
        print('Messages:')
        for message in vessel_line_rupture_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (len(vessel_line_rupture_calculation.discharge_records) != 2):
            assert False,f'Regression failed with len(vessel_line_rupture_calculation.discharge_records) = {len(vessel_line_rupture_calculation.discharge_records)}'
        if (abs((vessel_line_rupture_calculation.discharge_records[0].mass_flow - 0.8312460349563479) /  0.8312460349563479) > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_calculation.discharge_records[0].mass_flow = {vessel_line_rupture_calculation.discharge_records[0].mass_flow}'
        if (abs((vessel_line_rupture_calculation.discharge_records[0].final_state.temperature - 280.0421759165028) / 280.0421759165028) > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_calculation.discharge_records[0].final_state.temperature = {vessel_line_rupture_calculation.discharge_records[0].final_state.temperature}'
        if (abs((vessel_line_rupture_calculation.discharge_records[0].final_velocity - 3.569757805283587) / 3.569757805283587) > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_calculation.discharge_records[0].final_velocity = {vessel_line_rupture_calculation.discharge_records[0].final_velocity}'
        if (abs((vessel_line_rupture_calculation.discharge_result.release_mass - 2750.746981948948) / 2750.746981948948) > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_calculation.discharge_result.release_mass = {vessel_line_rupture_calculation.discharge_result.release_mass }'
        print(f'vessel_line_rupture_calculation.discharge_result.release_mass: {vessel_line_rupture_calculation.discharge_result.release_mass} [kg]')
        print(f'SUCCESS: vessel_line_rupture_calculation ({vessel_line_rupture_calculation.calculation_elapsed_time}ms)')
        print(f'final velocity = {vessel_line_rupture_calculation.discharge_records[0].final_velocity}')
    else:
        assert False, f'FAILED vessel_line_rupture_calculation with result code {resultCode}'
