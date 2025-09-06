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
    FireballCalculation,
    RadiationTransectCalculation,
    VesselCatastrophicRuptureCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    DischargeParameters,
    FlammableOutputConfig,
    FlammableParameters,
    LocalPosition,
    Material,
    MaterialComponent,
    State,
    Transect,
    Vessel,
    Weather,
)
from pypws.enums import AtmosphericStabilityClass, Resolution, ResultCode, VesselShape


def test_case_90():
    material = Material("ETHANE_BUTANE_PROPANE", [MaterialComponent("ETHANE", 0.5), MaterialComponent("N-BUTANE", 0.3), MaterialComponent("PROPANE", 0.2)], component_count = 3)
    state = State(temperature=265.0, pressure= 5.0e5, liquid_fraction=0.8)

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
        
    exit_material = vessel_catastrophic_rupture_calculation.exit_material

    # Define the weather.
    weather = Weather(wind_speed = 2.0, stability_class = AtmosphericStabilityClass.STABILITY_E)

    # Create a fireball calculation based on the vessel catastrophic rupture calculation and weather.
    fireball_calculation = FireballCalculation(discharge_records = vessel_catastrophic_rupture_calculation.discharge_records, discharge_record_count = len(vessel_catastrophic_rupture_calculation.discharge_records), discharge_result = vessel_catastrophic_rupture_calculation.discharge_result, weather = weather, material = exit_material, state = state)

    # Run the calculation
    print('Running fireball_calculation...')
    resultCode = fireball_calculation.run()

    # Print any messages.
    if len(fireball_calculation.messages) > 0:
        print('Messages:')
        for message in fireball_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        print(f'SUCCESS: fireball_calculation ({fireball_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED fireball_calculation with result code {resultCode}'

    # Define the radiation resolution.
    radiation_resolution = Resolution.MEDIUM

    # Define the transect
    transect = Transect(transect_start_point = LocalPosition(10.0, 0.0, 5.0), transect_end_point = LocalPosition(100.0, 0.0, 5.0))

    # Create flammable output configurations.
    flammable_output_config = FlammableOutputConfig(position = LocalPosition(), transect = transect, radiation_resolution= radiation_resolution)

    # Create a radiation transect calculation using the flame result, flame records, weather, flammable parameters, and flammable output configurations.
    radiation_transect_calculation = RadiationTransectCalculation(flame_result=fireball_calculation.flame_result,flame_records=fireball_calculation.flame_records, flame_record_count=len(fireball_calculation.flame_records), weather=weather, flammable_parameters=FlammableParameters(), flammable_output_config=flammable_output_config)

    # Run the radiation transect calculation.
    print('Running radiation_transect_calculation...')
    result_code = radiation_transect_calculation.run()

    # Print any messages.
    if len(radiation_transect_calculation.messages) > 0:
        print('Messages:')
        for message in radiation_transect_calculation.messages:
            print(message)

    if result_code == ResultCode.SUCCESS:
        if (abs((fireball_calculation.flame_result.flame_diameter- 31.624965667724611)/31.62496566772461) > 1e-3):
            assert False,f'Regression failed with fireball_calculation.flame_result.flame_diameter = {fireball_calculation.flame_result.flame_diameter}'    
        if (len(radiation_transect_calculation.radiation_records) != 50):
            assert False,f'Regression failed with len(radiation_transect_calculation.radiation_records) = {len(radiation_transect_calculation.radiation_records)}'
        if (abs((radiation_transect_calculation.radiation_records[0].radiation_result - 36402.50812563037)/36402.50812563037)> 1e-3):
            assert False,f'Regression failed with radiation_transect_calculation.radiation_records[0].radiation_result = {radiation_transect_calculation.radiation_records[0].radiation_result}'
        print(f'SUCCESS: radiation_transect_calculation ({radiation_transect_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED radiation_transect_calculation with result code {result_code}'