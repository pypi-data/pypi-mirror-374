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
    LateExplosionCalculation,
    VesselLineRuptureCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    DischargeParameters,
    DispersionOutputConfig,
    DispersionParameters,
    ExplosionConfinedVolume,
    ExplosionOutputConfig,
    ExplosionParameters,
    LineRupture,
    Material,
    MaterialComponent,
    State,
    Substrate,
    Vessel,
    Weather,
)
from pypws.enums import (
    AtmosphericStabilityClass,
    MEConfinedMethod,
    ResultCode,
    SpecialConcentration,
    VesselShape,
    WindProfileFlag
)


def test_78():

    # Define the initial state of the vessel.
    state = State(temperature=250.0, pressure=float(3.0e5), liquid_fraction=1.0)

    # Define the material contained by the vessel.
    material = Material("PROPANE", [MaterialComponent("PROPANE", 1.0)])

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

    # Create a vessel to use in the line rupture calculation using the previously defined entities. The vessel is a horizontal cylinder with a diameter of 2m and a length of 5m.
    vessel = Vessel(state=state, material=material, vessel_conditions=vessel_state_calculation.vessel_conditions, liquid_fill_fraction_by_volume=0.7, shape=VesselShape.HORIZONTAL_CYLINDER, diameter=2, length=5)

    # Create a line rupture to use in the vessel line rupture calculation.Pipe diameter is 0.1m, pipe length is 5m, and pipe height fraction is 0.3.
    line_rupture = LineRupture(pipe_diameter=0.1, pipe_length=5.0, pipe_height_fraction=0.3)

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
        print(f'SUCCESS: vessel_line_rupture_calculation ({vessel_line_rupture_calculation.calculation_elapsed_time}ms)')
        print(f'vessel_line_rupture_calculation.discharge_result.release_mass: {vessel_line_rupture_calculation.discharge_result.release_mass} [kg]')
    else:
        assert False, f'FAILED vessel_line_rupture_calculation with result code {resultCode}'
        
    exit_material = vessel_line_rupture_calculation.exit_material

    # Define the weather.
    weather = Weather(wind_speed = 1.5, stability_class = AtmosphericStabilityClass.STABILITY_F, wind_profile_flag= WindProfileFlag.LOGARITHMIC_PROFILE)

    # Define the substrate.
    substrate = Substrate()

    # Create a dispersion calculation based on the vessel line rupture calculation, weather, substrate, and dispersion parameters.
    dispersion_calculation = DispersionCalculation(discharge_records = vessel_line_rupture_calculation.discharge_records, discharge_result = vessel_line_rupture_calculation.discharge_result, weather = weather, substrate = substrate, dispersion_parameters = DispersionParameters(), end_point_concentration = 0.0, discharge_record_count = len(vessel_line_rupture_calculation.discharge_records), material = material)

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
    explosion_output_config =  ExplosionOutputConfig(overpressure_level = 8272, me_confined_method = MEConfinedMethod.USER_DEFINED)

    # Define the explosion confined volume
    explosion_confined_volumes = [ExplosionConfinedVolume(confined_volume = 167, confined_strength = 9), ExplosionConfinedVolume(confined_volume = 33, confined_strength = 10), ExplosionConfinedVolume(confined_volume = 300, confined_strength = 6)]

    # Create an explosion calculation based on the dispersion calculation, weather, substrate, explosion parameters, explosion configs and explosion confined volumes.
    late_explosion_calculation = LateExplosionCalculation(material = material, scalar_udm_outputs = dispersion_calculation.scalar_udm_outputs, weather = weather, dispersion_records = dispersion_calculation.dispersion_records, dispersion_record_count = len(dispersion_calculation.dispersion_records), explosion_parameters = explosion_parameters, explosion_output_config = explosion_output_config, explosion_confined_volumes = explosion_confined_volumes, substrate = substrate, explosion_confined_volume_count = len(explosion_confined_volumes), dispersion_parameters = DispersionParameters(), dispersion_output_config = dispersion_output_config)

    # Run the calculation.
    print('Running late_explosion_calculation...')
    resultCode = late_explosion_calculation.run()

    # Print any messages.
    if len(late_explosion_calculation.messages) > 0:
        print('Messages:')
        for message in late_explosion_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        if (abs((late_explosion_calculation.explosion_unif_conf_overpressure_result.exploded_mass-1081.1427088939722)/1081.1427088939722)>1e-3):
            assert False,f'Regression failed with late_explosion_calculation.explosion_unif_conf_overpressure_result.exploded_mass = {late_explosion_calculation.explosion_unif_conf_overpressure_result.exploded_mass}'
        if (abs((late_explosion_calculation.explosion_unif_conf_overpressure_result.ignition_time-  96.0561524166236)/  96.0561524166236)>1e-3):
            assert False,f'Regression failed with late_explosion_calculation.explosion_unif_conf_overpressure_result.ignition_time = {late_explosion_calculation.explosion_unif_conf_overpressure_result.ignition_time}'
        if (abs((late_explosion_calculation.explosion_unif_conf_overpressure_result.maximum_distance- 272.08706213990797)/ 272.08706213990797)>1e-3):
            assert False,f'Regression failed with late_explosion_calculation.explosion_unif_conf_overpressure_result.maximum_distance = {late_explosion_calculation.explosion_unif_conf_overpressure_result.maximum_distance}'
        print(f'SUCCESS: late_explosion_calculation ({late_explosion_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED late_explosion_calculation with result code {resultCode}'