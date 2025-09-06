import os
import pathlib
import sys

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
    DispersionCalculation,
    LateExplosionToOPLevelsCalculation,
    VesselReliefValveCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    Bund,
    DischargeParameters,
    DispersionOutputConfig,
    DispersionParameters,
    ExplosionConfinedVolume,
    ExplosionOutputConfig,
    ExplosionParameters,
    Material,
    MaterialComponent,
    ReliefValve,
    State,
    Substrate,
    Vessel,
    Weather,
)
from pypws.enums import (
    AtmosphericStabilityClass,
    ResultCode,
    SpecialConcentration,
    VesselShape,
)


def test_48():

    # Define the initial state of the vessel.
    state = State(temperature=270.0, pressure=float(8e6), liquid_fraction=1.0)

    # Define the material contained by the vessel.
    material = Material("HYDROGEN", [MaterialComponent("HYDROGEN", 1.0)])

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

    # Create a vessel to use in the relief valve calculation using the previously defined entities. The vessel is a sphere with a diameter of 5m.
    vessel = Vessel(state=state, material=material, vessel_conditions=vessel_state_calculation.vessel_conditions, liquid_fill_fraction_by_volume=0.7, shape=VesselShape.VESSEL_SPHERE, diameter=5)

    # Create a relief valve to use in the relief valve calculation. Pipe diameter is 0.5m, pipe length is 1m, and pipe height fraction is 1.
    relief_valve = ReliefValve(pipe_diameter=0.5, pipe_length=1.0, pipe_height_fraction=1, relief_valve_constriction_diameter=0.25)

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
        print(f'SUCCESS: vessel_relief_valve_calculation ({vessel_relief_valve_calculation.calculation_elapsed_time}ms)')
        print(f'vessel_relief_valve_calculation.discharge_result.release_mass: {vessel_relief_valve_calculation.discharge_result.release_mass} [kg]')
    else:
        assert False, f'FAILED vessel_relief_valve_calculation with result code {resultCode}'

    exit_material = vessel_relief_valve_calculation.exit_material

    # Define the weather.
    weather = Weather(wind_speed = 1.5, stability_class = AtmosphericStabilityClass.STABILITY_F)

    # Define the substrate.
    substrate = Substrate()

    # Create a dispersion calculation based on the vessel relief valve calculation, weather, substrate, and dispersion parameters.
    dispersion_calculation = DispersionCalculation(discharge_records = vessel_relief_valve_calculation.discharge_records, discharge_result = vessel_relief_valve_calculation.discharge_result, weather = weather, substrate = substrate, dispersion_parameters = DispersionParameters(), end_point_concentration = 0.0, discharge_record_count = len(vessel_relief_valve_calculation.discharge_records), material = exit_material)

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

    # Define the dispersion output config
    dispersion_output_config = DispersionOutputConfig(concentration = 0.0, special_concentration = SpecialConcentration.MIN)    

    # Define the explosion parameters.
    explosion_parameters = ExplosionParameters(explosion_uniform_strength = 10.0) 

    # Define the explosion output configuration.
    explosion_output_configs = [ExplosionOutputConfig(overpressure_level = 1034), ExplosionOutputConfig(overpressure_level = 2068), ExplosionOutputConfig(overpressure_level = 4136)]

    # Define the explosion confined volume
    explosion_confined_volumes = [ExplosionConfinedVolume(), ExplosionConfinedVolume()]

    # Create an explosion calculation based on the dispersion calculation, weather, substrate, explosion parameters, explosion configs and explosion confined volumes.
    late_explosion_to_OP_levels_calculation = LateExplosionToOPLevelsCalculation(material = exit_material, scalar_udm_outputs = dispersion_calculation.scalar_udm_outputs, weather = weather, dispersion_records = dispersion_calculation.dispersion_records, dispersion_record_count = len(dispersion_calculation.dispersion_records), explosion_parameters = explosion_parameters, explosion_output_configs = explosion_output_configs, explosion_confined_volumes = explosion_confined_volumes, substrate = substrate, explosion_output_config_count = len(explosion_output_configs), explosion_confined_volume_count = len(explosion_confined_volumes), dispersion_parameters = DispersionParameters(), dispersion_output_config = dispersion_output_config)

    # Run the calculation.
    print('Running late_explosion_to_OP_levels_calculation...')
    resultCode = late_explosion_to_OP_levels_calculation.run()

    # Print any messages.
    if len(late_explosion_to_OP_levels_calculation.messages) > 0:
        print('Messages:')
        for message in late_explosion_to_OP_levels_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        if (abs((late_explosion_to_OP_levels_calculation.explosion_unif_conf_overpressure_results[0].exploded_mass - 364.4122308301167)/364.4122308301167)>1e-3):
            assert False,f'Regression failed with late_explosion_to_OP_levels_calculation.explosion_unif_conf_overpressure_results[0].exploded_mass = {late_explosion_to_OP_levels_calculation.explosion_unif_conf_overpressure_results[0].exploded_mass}'
        if (abs((late_explosion_to_OP_levels_calculation.explosion_unif_conf_overpressure_results[0].ignition_time - 4.444690161422924)/4.444690161422924)>1e-3):
            assert False,f'Regression failed with late_explosion_to_OP_levels_calculation.explosion_unif_conf_overpressure_results[0].ignition_time = {late_explosion_to_OP_levels_calculation.explosion_unif_conf_overpressure_results[0].ignition_time}'
        if (abs((late_explosion_to_OP_levels_calculation.explosion_unif_conf_overpressure_results[0].maximum_distance- 1024.8207387858251)/ 1024.8207387858251)>1e-3):
            assert False,f'Regression failed with late_explosion_to_OP_levels_calculation.explosion_unif_conf_overpressure_results[0].maximum_distance = {late_explosion_to_OP_levels_calculation.explosion_unif_conf_overpressure_results[0].maximum_distance}'
        print(f'SUCCESS: late_explosion_to_OP_levels_calculation ({late_explosion_to_OP_levels_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED late_explosion_to_OP_levels_calculation with result code {resultCode}'