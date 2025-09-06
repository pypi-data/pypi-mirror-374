import os
import pathlib
import sys
from pickle import GET

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


from pypws.calculations import (
    SetPhaseToReleaseForLeakScenarioCalculation,
    SetPhaseToReleaseForLineRuptureScenarioCalculation,
)
from pypws.entities import Material, MaterialComponent, State, Vessel
from pypws.enums import Phase, ResultCode, VesselConditions, VesselShape


def test_case_151():
    
    """
    Test for set phase to release for line rupture scenario calculation with the following inputs

        material_name = 'N-PENTANE+METHANE'
        state_temperature = 280.0
        state_pressure = 8.0E+05
        vessel_shape = VesselShape.VESSEL_SPHERE
        vessel_diameter = 3.0
        
    """

    # Define the material.
    material = Material(
        name="N-PENTANE+METHANE",
        components=[
            MaterialComponent(
                name="N-PENTANE",
                mole_fraction=0.5
            ),
            MaterialComponent(
                name="METHANE",
                mole_fraction=0.5
            )
        ],
        component_count = 2
    )

    # Define the properties.
    state_temperature = 280.0
    state_pressure = 8.0E+06
    vessel_shape = VesselShape.VESSEL_SPHERE
    vessel_diameter = 5.0

    # Create a vessel.
    vessel = Vessel(state = State(pressure= state_pressure, temperature = state_temperature, liquid_fraction = 0.8), material = material, diameter = vessel_diameter, shape = vessel_shape, vessel_conditions = VesselConditions.STRATIFIED_TWO_PHASE_VESSEL, liquid_fill_fraction_by_volume = 0.6)

    # Create a set phase to be released for line rupture calculation.
    set_phase_to_be_released_for_line_rupture_scenario_calculation = SetPhaseToReleaseForLineRuptureScenarioCalculation(vessel = vessel, release_elevation = 1.0, phase_to_release = Phase.LIQUID)

    # Run the calculation.
    print ('Running set_phase_to_be_released_for_line_rupture_scenario_calculation')
    result_code = set_phase_to_be_released_for_line_rupture_scenario_calculation.run()

    # Print any messages.
    if len(set_phase_to_be_released_for_line_rupture_scenario_calculation.messages) > 0:
        print('Messages:')
        for message in set_phase_to_be_released_for_line_rupture_scenario_calculation.messages:
            print(message)

    if result_code == ResultCode.SUCCESS:
        if (set_phase_to_be_released_for_line_rupture_scenario_calculation.phase_to_release != 3):
            assert False, f'Regression failed with set_phase_to_be_released_for_line_rupture_scenario_calculation with phase_to_release = {set_phase_to_be_released_for_line_rupture_scenario_calculation.phase_to_release}'
        if (abs((set_phase_to_be_released_for_line_rupture_scenario_calculation.pipe_height_fraction_updated - 0.5668689228522562)/0.5668689228522562)> 1e-3):
            assert False,f'Regression failed with set_phase_to_be_released_for_line_rupture_scenario_calculation with pipe_height_fraction_updated = {set_phase_to_be_released_for_line_rupture_scenario_calculation.pipe_height_fraction_updated}'
        print(f'SUCCESS: set_phase_to_be_released_for_line_rupture_scenario_calculation ({set_phase_to_be_released_for_line_rupture_scenario_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED set_phase_to_be_released_for_line_rupture_scenario_calculation with result code {result_code}'