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

from pypws.calculations import (
    DispersionCalculation,
    MaxConcDistanceCalculation,
    VesselCatastrophicRuptureCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    DischargeParameters,
    DispersionOutputConfig,
    DispersionParameters,
    Material,
    MaterialComponent,
    State,
    Substrate,
    Vessel,
    Weather,
)
from pypws.enums import (
    Resolution,
    ResultCode,
    SpecialConcentration,
    VesselShape,
    WindProfileFlag
)


def test_case_109():
    # Define the test case properties.
    material_name = 'HYDROGEN'
    end_point_concentration = 0.0
    elevation = 10.0
    resolution = Resolution.MEDIUM
    special_concentration = SpecialConcentration.LFL_FRACTION
    lfl_fraction = 0.7
    component_to_track_name = ''

    # Define the material
    material = Material(name = material_name, components = [MaterialComponent(name = material_name)])
    state = State(temperature=265.0, pressure= 5.0e5, liquid_fraction=0.0)

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

    vessel = Vessel(state=state,
                    material=material,
                    liquid_fill_fraction_by_volume=0.8,
                    shape=VesselShape.VERTICAL_CYLINDER,
                    vessel_conditions = vessel_state_calculation.vessel_conditions
                    )

    discharge_parameters = DischargeParameters()

    vessel_catastrophic_rupture_calculation = VesselCatastrophicRuptureCalculation(vessel, discharge_parameters)

    print('Running vessel_catastrophic_rupture_calculation...')
    resultCode = vessel_catastrophic_rupture_calculation.run()

    # Print any messages.
    if len(vessel_catastrophic_rupture_calculation.messages) > 0:
        print('Messages:')
        for message in vessel_catastrophic_rupture_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        print(f'SUCCESS: vessel_catastrophic_rupture_calculation ({vessel_catastrophic_rupture_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED vessel_catastrophic_rupture_calculation with result code {resultCode}'

    # Set up the entities required by the dispersion calculation.
    substrate = Substrate()
    weather = Weather(wind_profile_flag=WindProfileFlag.LOGARITHMIC_PROFILE)
    dispersion_parameters = DispersionParameters()

    # Set up the dispersion calculation.
    dispersion_calculation = DispersionCalculation(vessel_catastrophic_rupture_calculation.exit_material, substrate, vessel_catastrophic_rupture_calculation.discharge_result, vessel_catastrophic_rupture_calculation.discharge_records, len(vessel_catastrophic_rupture_calculation.discharge_records), weather, dispersion_parameters, end_point_concentration)

    print('Running dispersion_calculation...')
    resultCode = dispersion_calculation.run()

    # Print any messages.
    if len(dispersion_calculation.messages) > 0:
        print('Messages:')
        for message in dispersion_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        print(f'SUCCESS: dispersion_calculation ({dispersion_calculation.calculation_elapsed_time}ms)')
        print(f'length dispersion records = {len(dispersion_calculation.dispersion_records)}')
        print(f'minimum concentration = {dispersion_calculation.scalar_udm_outputs.minimum_concentration}')
        print(f'observer count = {dispersion_calculation.scalar_udm_outputs.observer_count}')
        print(f'final centreline concentration = {dispersion_calculation.dispersion_records[len(dispersion_calculation.dispersion_records)-1].centreline_concentration}')
        print(f'final downwind distance = {dispersion_calculation.dispersion_records[len(dispersion_calculation.dispersion_records)-1].downwind_distance}')
        print(f'SUCCESS: dispersion_calculation ({dispersion_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED dispersion_calculation with result code {resultCode}'

    # Set up the entities required by the maximum concentration footprint calculation.
    dispersion_output_config = DispersionOutputConfig(concentration = end_point_concentration,
                                                    elevation = elevation,
                                                    resolution = resolution,
                                                    special_concentration = special_concentration,
                                                    lfl_fraction_value = lfl_fraction,
                                                    component_to_track_name = component_to_track_name)

    # Create a max concentration distance calculation using the dispersion calculation and the dispersion output config.
    max_conc_distance_calculation = MaxConcDistanceCalculation(scalar_udm_outputs = dispersion_calculation.scalar_udm_outputs,
                                                            dispersion_records= dispersion_calculation.dispersion_records,
                                                            dispersion_record_count= len(dispersion_calculation.dispersion_records),
                                                            weather= weather,
                                                            substrate= substrate,
                                                            dispersion_output_config= dispersion_output_config,
                                                            material= vessel_catastrophic_rupture_calculation.exit_material,
                                                            dispersion_parameters= dispersion_parameters)

    # Run the max concentration distance calculation.
    print('Running max_conc_distance_calculation...')
    resultCode = max_conc_distance_calculation.run()

    # Print any messages.
    if len(max_conc_distance_calculation.messages) > 0:
        print('Messages:')
        for message in max_conc_distance_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        if (len(max_conc_distance_calculation.concentration_records) >0):
            if (abs((max_conc_distance_calculation.concentration_records[len(max_conc_distance_calculation.concentration_records)-1].concentration-0.02586928069095842)/0.02586928069095842) > 1e-3):
                assert False,f'Regression failed with max_conc_distance_calculation.concentration_records[len(max_conc_distance_calculation.concentration_records)-1].concentration = {max_conc_distance_calculation.concentration_records[len(max_conc_distance_calculation.concentration_records)-1].concentration}'
        if (len(max_conc_distance_calculation.concentration_records) != 6):
            assert False,f'Regression failed with len(max_conc_distance_calculation.concentration_records) = {len(max_conc_distance_calculation.concentration_records)}'
        if (len(max_conc_distance_calculation.concentration_records) >0):
            if (abs((max_conc_distance_calculation.concentration_records[len(max_conc_distance_calculation.concentration_records)-1].position.x-26.782730275398364)/26.782730275398364) > 1e-3):
                assert False,f'Regression failed with max_conc_distance_calculation.concentration_records[len(max_conc_distance_calculation.concentration_records)-1].position.x = {max_conc_distance_calculation.concentration_records[len(max_conc_distance_calculation.concentration_records)-1].position.x}'
        print(f'SUCCESS: max_conc_distance_calculation ({max_conc_distance_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED max_conc_distance_calculation with result code {resultCode}'