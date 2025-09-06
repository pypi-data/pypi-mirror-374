import os
import pathlib
import sys

PYPWS_RUN_LOCALLY = os.getenv('PYPWS_RUN_LOCALLY')
if PYPWS_RUN_LOCALLY and PYPWS_RUN_LOCALLY.lower() == 'true':
    # Navigate to the PYPWS directory by searching upwards until it is found.
    current_dir = pathlib.Path(__file__).resolve()

    while current_dir.name.lower() != 'package':
        current_dir = current_dir.parent

    # Insert the path to the pypws package into sys.path.
    sys.path.insert(0, f'{current_dir}')


from pypws.calculations import (
    DispersionCalculation,
    PoolFireCalculation,
    RadiationAtPointsForPoolFiresCalculation,
    VesselCatastrophicRuptureCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    Bund,
    DischargeParameters,
    DispersionParameters,
    FlammableOutputConfig,
    FlammableParameters,
    LocalPosition,
    Material,
    MaterialComponent,
    State,
    Substrate,
    Transect,
    Vessel,
    Weather,
)
from pypws.enums import (
    AtmosphericStabilityClass,
    PoolFireType,
    PropertyTemplate,
    ResultCode,
    VesselConditions,
    VesselShape,
)


def test_44a():

    # Define material and state.
    material = Material("AMMONIA", [MaterialComponent("AMMONIA", 1.0)])
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
                    vessel_conditions = vessel_state_calculation.vessel_conditions
                    )

    distcharge_parameters = DischargeParameters()


    vessel_catastrophic_rupture_calculation = VesselCatastrophicRuptureCalculation(vessel, distcharge_parameters)

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

    # Define the weather.
    weather = Weather(wind_speed = 10.0, stability_class = AtmosphericStabilityClass.STABILITY_A)

    # Define the substrate.
    substrate = Substrate()

    # Create a dispersion calculation based on the vessel catastrophic rupture calculation, weather, substrate, and dispersion parameters.
    dispersion_calculation = DispersionCalculation(discharge_records = vessel_catastrophic_rupture_calculation.discharge_records, discharge_result = vessel_catastrophic_rupture_calculation.discharge_result, weather = weather, substrate = substrate, dispersion_parameters = DispersionParameters(), end_point_concentration = 0.0, discharge_record_count = len(vessel_catastrophic_rupture_calculation.discharge_records), material = vessel_catastrophic_rupture_calculation.exit_material)

    # Run the calculation.
    print('Running dispersion_calculation...')
    resultCode = dispersion_calculation.run()

    # Print any messages.
    if len(dispersion_calculation.messages) > 0:
        print('Messages:')
        for message in dispersion_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        print(f'SUCCESS: dispersion_calculation_calculation ({dispersion_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED dispersion_calculation with result code {resultCode}'

    # Define a flammable parameter set.
    flammable_parameters = FlammableParameters(pool_fire_type = PoolFireType.EARLY)

    # Create a pool fire calculation based on the dispersion calculation, weather, substrate, and flammable parameters.
    pool_fire_calculation = PoolFireCalculation(material = vessel_catastrophic_rupture_calculation.exit_material, pool_records = dispersion_calculation.pool_records, pool_record_count = len(dispersion_calculation.pool_records), weather = weather, substrate = substrate, flammable_parameters = flammable_parameters)

    # Run the calculation.
    print('Running pool_fire_calculation...')
    resultCode = pool_fire_calculation.run()

    # Print any messages.
    if len(pool_fire_calculation.messages) > 0:
        print('Messages:')
        for message in pool_fire_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        print(f'SUCCESS: pool_fire_calculation ({pool_fire_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED pool_fire_calculation with result code {resultCode}'

    # Define a flammable output config.
    flammable_output_configs = [FlammableOutputConfig(position = LocalPosition(0.0, 0.0, 0.0)), FlammableOutputConfig(position = LocalPosition(0.0, 0.0, 1.0)), FlammableOutputConfig(position = LocalPosition(0.0, 0.0, 2.0))]

    # Create a radiation a points calculation based on the pool fire calculation, weather, substrate, and flammable output config.
    radiation_at_points_for_pool_fires_calculation = RadiationAtPointsForPoolFiresCalculation(flame_records = pool_fire_calculation.flame_records, pool_fire_flame_result = pool_fire_calculation.pool_fire_flame_result, flame_record_count = len(pool_fire_calculation.flame_records), flammable_output_configs = flammable_output_configs, weather = weather, flammable_parameters = flammable_parameters, flammable_output_config_count = len (flammable_output_configs))    

    # Run the calculation.
    print('Running radiation_at_points_for_pool_fires_calculation...')
    resultCode = radiation_at_points_for_pool_fires_calculation.run()

    # Print any messages.
    if len(radiation_at_points_for_pool_fires_calculation.messages) > 0:
        print('Messages:')
        for message in radiation_at_points_for_pool_fires_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        if (abs((radiation_at_points_for_pool_fires_calculation.radiation[0]-33916.10546875)/33916.10546875)>1e-3):
            assert False,f'Regression failed with radiation value {radiation_at_points_for_pool_fires_calculation.radiation[0]}'
        if (abs((radiation_at_points_for_pool_fires_calculation.pool_fire_flame_result.flame_diameter-41.44367599487305)/41.44367599487305)>1e-3):
            assert False,f'Regression failed with flame diameter value {radiation_at_points_for_pool_fires_calculation.pool_fire_flame_result.flame_diameter}'
        print(f'SUCCESS: radiation_at_points_for_pool_fires_calculation ({radiation_at_points_for_pool_fires_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED radiation_at_points_for_pool_fires_calculation with result code {resultCode}'
