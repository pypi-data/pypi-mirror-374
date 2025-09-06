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

from pypws.calculations import TankFireCalculation
from pypws.entities import (
    AtmosphericStorageTank,
    FlammableParameters,
    Material,
    MaterialComponent,
    State,
    Substrate,
    Weather,
)
from pypws.enums import AtmosphericStabilityClass, PoolFireType, ResultCode


def test_case_83():
    # Set the case properties.
    material_name = "N-HEPTANE_N-OCTANE"
    diameter = 3.0
    height = 10.0
    wind_speed = 1.0
    fire_type = PoolFireType.LATE
    weather_stability = AtmosphericStabilityClass.STABILITY_C

    # Define the initial state of the tank.
    state = State(temperature = 290.0, pressure = 1.0E+06, liquid_fraction = 0.0)

    # Define the material contained by the tank.
    material = Material(material_name, [MaterialComponent("N-HEPTANE", 0.4), MaterialComponent("N-OCTANE", 0.6)], component_count=2)

    # Define the weather conditions
    weather = Weather(wind_speed=wind_speed, stability_class=weather_stability)

    # Define the substrate
    substrate = Substrate()

    # Define the flammable parameters
    flammable_parameters = FlammableParameters(pool_fire_type=fire_type)

    # Define the conditions of the tank
    tank= AtmosphericStorageTank(state=state, material=material, diameter=diameter, height=height)

    # Create the TankFireCalculation object
    tank_fire_calculation = TankFireCalculation(atmospheric_storage_tank=tank, weather=weather, substrate=substrate, flammable_parameters=flammable_parameters)

    # Run the calculation
    print("Running the calculation...")
    result_code = tank_fire_calculation.run()

    # Print any messages
    if len(tank_fire_calculation.messages) > 0:
            print('Messages:')
            for message in tank_fire_calculation.messages:
                print(message)

    if result_code == ResultCode.SUCCESS:
        if (abs((tank_fire_calculation.pool_fire_flame_result.surface_emissive_power - 103709.09375) / 103709.09375) > 1e-3):
            assert False,f'Regression failed with tank_fire_calculation.pool_fire_flame_result.surface_emissive_power = {tank_fire_calculation.pool_fire_flame_result.surface_emissive_power}'
        if (abs((tank_fire_calculation.pool_fire_flame_result.flame_length - 8.156496047973633) / 8.156496047973633) > 1e-3):
            assert False,f'Regression failed with tank_fire_calculation.pool_fire_flame_result.flame_length = {tank_fire_calculation.pool_fire_flame_result.flame_length}'
        print(f'SUCCESS: tank_fire_calculation ({tank_fire_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED tank_fire_calculation with result code {result_code}'