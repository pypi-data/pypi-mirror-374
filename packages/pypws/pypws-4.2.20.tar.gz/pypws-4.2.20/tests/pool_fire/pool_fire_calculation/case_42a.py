import os
import pathlib
import sys

# When running locally the environment variable RUN_LOCALLY needs to be set to True.
# Check if the environment variable is set
if os.getenv('PYPWS_RUN_LOCALLY') != None and os.getenv('PYPWS_RUN_LOCALLY').lower() == 'true':
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
    VesselLeakCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    Bund,
    DischargeParameters,
    DispersionParameters,
    FlammableOutputConfig,
    FlammableParameters,
    Leak,
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
    ResultCode,
    TimeVaryingOption,
    VesselShape,
)

"""
This sample demonstrates how to use the vessel leak calculation along with with the dependent entities.
"""

def case_42a():

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
        print(f'SUCCESS: vessel_leak_calculation ({vessel_leak_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED vessel_leak_calculation with result code {resultCode}'
        
    # Define the weather.
    weather = Weather(wind_speed = 2.0, stability_class = AtmosphericStabilityClass.STABILITY_E)

    # Define the substrate.
    substrate = Substrate()

    # Create a dispersion calculation based on the vessel catastrophic rupture calculation, weather, substrate, and dispersion parameters.
    dispersion_calculation = DispersionCalculation(discharge_records = vessel_leak_calculation.discharge_records, discharge_result = vessel_leak_calculation.discharge_result, weather = weather, substrate = substrate, dispersion_parameters = DispersionParameters(), end_point_concentration = 0.0, discharge_record_count = len(vessel_leak_calculation.discharge_records), material =  vessel_leak_calculation.exit_material)

    # Run the calculation.
    print('Running dispersion_calculation...')
    resultCode = dispersion_calculation.run()

    # Print any messages.
    if len(dispersion_calculation.messages) > 0:
        print('Messages:')
        for message in dispersion_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        print(f'SUCCESS: dispersion_calculation ({dispersion_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED dispersion_calculation with result code {resultCode}'

    # Define a flammable parameter set.
    flammable_parameters = FlammableParameters(pool_fire_type = PoolFireType.LATE)

    # Create a pool fire calculation based on the dispersion calculation, weather, substrate, and flammable parameters.
    pool_fire_calculation = PoolFireCalculation(material =  vessel_leak_calculation.exit_material, pool_records = dispersion_calculation.pool_records, pool_record_count = len(dispersion_calculation.pool_records), weather = weather, substrate = substrate, flammable_parameters = flammable_parameters)

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
        if (abs((radiation_at_points_for_pool_fires_calculation.radiation[0]-138315.75)/138315.75)>1e-3):
            assert False,f'Regression failed with radiation value {radiation_at_points_for_pool_fires_calculation.radiation[0]}'
        if (abs((radiation_at_points_for_pool_fires_calculation.pool_fire_flame_result.flame_diameter-36.82126235961914)/36.82126235961914)>1e-3):
            assert False,f'Regression failed with flame diameter value {radiation_at_points_for_pool_fires_calculation.pool_fire_flame_result.flame_diameter}'
        print(f'SUCCESS: radiation_at_points_for_pool_fires_calculation ({radiation_at_points_for_pool_fires_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED radiation_at_points_for_pool_fires_calculation with result code {resultCode}'
