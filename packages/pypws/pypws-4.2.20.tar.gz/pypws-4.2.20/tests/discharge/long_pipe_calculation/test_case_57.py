import os
import pathlib
import sys

run_locally = os.getenv('PYPWS_RUN_LOCALLY')
if run_locally and run_locally.lower() == 'true':
    # Navigate to the PYPWS directory by searching upwards until it is found.
    current_dir = pathlib.Path(__file__).resolve()

    while current_dir.name.lower() != 'package':
        if current_dir.parent == current_dir:  # Check if the current directory is the root directory
            raise FileNotFoundError("The 'pypws' directory was not found in the path hierarchy.")
        current_dir = current_dir.parent

    # Insert the path to the pypws package into sys.path.
    sys.path.insert(0, f'{current_dir}')

from pypws.calculations import LongPipeBreachCalculation
from pypws.entities import (
    DischargeParameters,
    LocalPosition,
    Material,
    MaterialComponent,
    Pipe,
    PipeBreach,
    State,
)
from pypws.enums import ResultCode


def test_case_57():

    material_name = "CARBON DIOXIDE (TOXIC)"
    # Define the material in the pipe.
    material = Material(material_name, [MaterialComponent(material_name, 1.0)])

    # Define the state of the fluid in the pipe.
    state = State(temperature=300.0, pressure= 1.0e6, liquid_fraction=0.0)

    # Define the pipe nodes.
    nodes = [LocalPosition(), LocalPosition(500, 10, 0)]


    # Define the pipe.
    pipe = Pipe(state=state,
                material=material,
                diameter=1.0,
                nodes = nodes,
                node_count = len(nodes),
                roughness=0.0001,
                pumped_inflow = 1.0
                )

    # Create a pipe breach.
    pipe_breach = PipeBreach(relative_aperture = 0.5, distance_downstream = 200)

    # Create the discharge parameters.
    discharge_parameters = DischargeParameters()

    # Create a long pipe breach calculation using the pipe, pipe breach and discharge parameters.
    long_pipe_breach_calculation = LongPipeBreachCalculation(pipe = pipe, pipe_breach = pipe_breach, discharge_parameters = discharge_parameters)

    # Run the long_pipe_breach_calculation.
    print('Running long_pipe_breach_calculation...')
    resultCode = long_pipe_breach_calculation.run()

    # Print any messages.
    if len(long_pipe_breach_calculation.messages) > 0:
        print('Messages:')
        for message in long_pipe_breach_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (abs((long_pipe_breach_calculation.discharge_records[1].mass_flow-3296.332186434568)/3296.332186434568)>1e-3):
            assert False,f'Regression failed with long_pipe_breach_calculation.discharge_records[1].mass_flow = {long_pipe_breach_calculation.discharge_records[1].mass_flow}'
        if (len(long_pipe_breach_calculation.discharge_records)!=100):
            assert False,f'Regression failed with len(long_pipe_breach_calculation.discharge_records) = {len(long_pipe_breach_calculation.discharge_records)}'
        if (len(long_pipe_breach_calculation.discharge_records)>0):
            if (abs((long_pipe_breach_calculation.discharge_records[len(long_pipe_breach_calculation.discharge_records)-1].time- 3600.0)/ 3600.0)>1e-3):
                assert False,f'Regression failed with long_pipe_breach_calculation.discharge_records[len(long_pipe_breach_calculation.discharge_records)-1].time = {long_pipe_breach_calculation.discharge_records[len(long_pipe_breach_calculation.discharge_records)-1].time}'
        if (abs((long_pipe_breach_calculation.discharge_result.release_mass- 10146.339556422015)/ 10146.339556422015)>1e-3):    
            assert False,f'Regression failed with long_pipe_breach_calculation.discharge_result.release_mass = {long_pipe_breach_calculation.discharge_result.release_mass}'
        print(f'SUCCESS: long_pipe_breach_calculation ({long_pipe_breach_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED long_pipe_breach_calculation with result code {resultCode}'

