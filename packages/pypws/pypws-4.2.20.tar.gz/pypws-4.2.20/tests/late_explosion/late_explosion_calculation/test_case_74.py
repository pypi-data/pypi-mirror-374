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
    VesselCatastrophicRuptureCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    DischargeParameters,
    DispersionOutputConfig,
    DispersionParameters,
    ExplosionConfinedVolume,
    ExplosionOutputConfig,
    ExplosionParameters,
    Material,
    MaterialComponent,
    State,
    Substrate,
    Vessel,
    Weather,
)
from pypws.enums import (
    AtmosphericStabilityClass,
    ResultCode,
    SpecialConcentration,
    WindProfileFlag
)


def test_74():

    # Define the material contained by the vessel.
    material = Material("N-HEXANE", [MaterialComponent("N-HEXANE", 1.0)])

    # Define the initial state of the vessel.
    state = State(temperature=280.0, pressure= 2.0e5, liquid_fraction=0.8)

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

    # Create a vessel to use in the vessel catastrophic rupture calculation using the previously defined entities.
    vessel = Vessel(state=state,
                    material=material,
                    liquid_fill_fraction_by_volume=0.8,
                    vessel_conditions = vessel_state_calculation.vessel_conditions
                    )

    # Define the discharge parameters for the vessel catastrophic rupture calculation.
    discharge_parameters = DischargeParameters()

    # Create a vessel catastrophic rupture calculation using the vessel and discharge parameters.
    vessel_catastrophic_rupture_calculation = VesselCatastrophicRuptureCalculation(vessel, discharge_parameters)

    # Run the calculation.
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
    weather = Weather(wind_speed = 1.5, stability_class = AtmosphericStabilityClass.STABILITY_F, wind_profile_flag= WindProfileFlag.LOGARITHMIC_PROFILE)

    # Define the substrate.
    substrate = Substrate()

    # Create a dispersion calculation based on the vessel catastrophic rupture calculation, weather, substrate, and dispersion parameters.
    dispersion_calculation = DispersionCalculation(discharge_records = vessel_catastrophic_rupture_calculation.discharge_records, discharge_result = vessel_catastrophic_rupture_calculation.discharge_result, weather = weather, substrate = substrate, dispersion_parameters = DispersionParameters(), end_point_concentration = 0.0, discharge_record_count = 1, material = exit_material)

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
    explosion_parameters = ExplosionParameters(explosion_uniform_strength = 7.0) 

    # Define the explosion output configuration.
    explosion_output_config = ExplosionOutputConfig(overpressure_level = 2068)

    # Define the explosion confined volume
    explosion_confined_volumes = [ExplosionConfinedVolume(), ExplosionConfinedVolume()]

    # Create an explosion calculation based on the dispersion calculation, weather, substrate, explosion parameters, explosion configs and explosion confined volumes.
    late_explosion_calculation = LateExplosionCalculation(material = exit_material, scalar_udm_outputs = dispersion_calculation.scalar_udm_outputs, weather = weather, dispersion_records = dispersion_calculation.dispersion_records, dispersion_record_count = len(dispersion_calculation.dispersion_records), explosion_parameters = explosion_parameters, explosion_output_config = explosion_output_config, explosion_confined_volumes = explosion_confined_volumes, substrate = substrate, explosion_confined_volume_count = len(explosion_confined_volumes), dispersion_parameters = DispersionParameters(), dispersion_output_config = dispersion_output_config)

    # Run the calculation.
    print('Running late_explosion_calculation...')
    resultCode = late_explosion_calculation.run()

    # Print any messages.
    if len(late_explosion_calculation.messages) > 0:
        print('Messages:')
        for message in late_explosion_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        if (abs((late_explosion_calculation.explosion_unif_conf_overpressure_result.exploded_mass-9.863701824923115)/9.863701824923115)>1e-3):
            assert False,f'Regression failed with late_explosion_calculation.explosion_unif_conf_overpressure_result.exploded_mass = {late_explosion_calculation.explosion_unif_conf_overpressure_result.exploded_mass}'
        if (abs((late_explosion_calculation.explosion_unif_conf_overpressure_result.ignition_time-5.794506457215323)/5.794506457215323)>1e-3):
            assert False,f'Regression failed with late_explosion_calculation.explosion_unif_conf_overpressure_result.ignition_time = {late_explosion_calculation.explosion_unif_conf_overpressure_result.ignition_time}'
        if (abs((late_explosion_calculation.explosion_unif_conf_overpressure_result.maximum_distance-112.78500368023822)/112.78500368023822)>1e-3):
            assert False,f'Regression failed with late_explosion_calculation.explosion_unif_conf_overpressure_result.maximum_distance = {late_explosion_calculation.explosion_unif_conf_overpressure_result.maximum_distance}'
        print(f'SUCCESS: late_explosion_calculation ({late_explosion_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED late_explosion_calculation with result code {resultCode}'