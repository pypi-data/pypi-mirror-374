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

from pypws.calculations import UserDefinedSourceLinkedRunCalculation
from pypws.entities import Material, MaterialComponent, Weather, Substrate, DischargeParameters, FlammableParameters, DispersionParameters, FlammableParameters, ExplosionParameters, ExplosionOutputConfig, ExplosionConfinedVolume, FlammableOutputConfig, DispersionOutputConfig, ExplosionConfinedVolume, State, DischargeRecord, DischargeResult, DischargeParameters, DispersionParameters, DispersionOutputConfig, ExplosionOutputConfig, FlammableOutputConfig
from pypws.enums import ResultCode, AtmosphericStabilityClass, SpecialConcentration, WindProfileFlag, Phase, FluidSpec, DynamicType

def test_vlr_154():

    material = Material("N-HEXANE", [MaterialComponent("N-HEXANE", 1.0)], component_count = 1)

    # Define the weather conditions
    weather = Weather(wind_speed=10.0, stability_class=AtmosphericStabilityClass.STABILITY_A, wind_profile_flag=WindProfileFlag.LOGARITHMIC_PROFILE)

    # Define the substrate
    substrate = Substrate()

    # Define the dispersion parameters
    dispersion_parameters = [DispersionParameters(averaging_time=18.75), DispersionParameters(averaging_time=600.0)]

    # Define the dispersion output configuration
    dispersion_output_configs_flammable = [DispersionOutputConfig(special_concentration=SpecialConcentration.LFL_FRACTION, elevation=1.0)]
    dispersion_output_configs_toxic = [DispersionOutputConfig(special_concentration=SpecialConcentration.MIN, elevation=0.0)]

    # Define the flammable parameters
    flammable_parameters = FlammableParameters()

    # Define the flammable output configuration
    flammable_output_configs = [FlammableOutputConfig()]

    # Define the explosion parameters
    explosion_parameters = ExplosionParameters()

    # Define the explosion output configuration
    explosion_output_configs = [ExplosionOutputConfig()]

    # Define the explosion confined volumes
    explosion_confined_volumes = [ExplosionConfinedVolume()]

    user_defined_source_linked_run_calculation = UserDefinedSourceLinkedRunCalculation(
        material=material,
        phase_to_be_released= Phase.LIQUID,
        discharge_records = [DischargeRecord(mass_flow = 100.0, time = 360.0, final_state = State(temperature =200.0, pressure = 101325.0, flash_flag = FluidSpec.TP, liquid_fraction= 1.0), orifice_state=State(pressure = 101325, temperature=300, liquid_fraction= 1.0), orifice_velocity= 0.0, storage_state=State(pressure = 101325, temperature=300, liquid_fraction=1.0), final_velocity= 60.0, droplet_diameter = 0.0015)],
        discharge_record_count = 1, 
        discharge_result= DischargeResult(release_mass = 3000.0, height = 1.0, angle = -0.30, hole_diameter= 0.3, release_type=DynamicType.CONTINUOUS, pre_dilution_air_rate=0.0, expansion_energy=6000.0),
        discharge_parameters= DischargeParameters(),
        substrate= substrate,
        weather= weather,
        dispersion_parameters= dispersion_parameters,
        dispersion_parameter_count=2,
        flammable_parameters= flammable_parameters,
        explosion_parameters= explosion_parameters,
        explosion_output_configs= explosion_output_configs,
        explosion_output_config_count= 1,
        explosion_confined_volumes= explosion_confined_volumes,
        explosion_confined_volume_count = 1,
        flammable_output_configs= flammable_output_configs,
        flammable_output_config_count = 1,
        dispersion_flam_output_configs=dispersion_output_configs_flammable,
        dispersion_flam_output_config_count= 1,
        dispersion_toxic_output_configs= dispersion_output_configs_toxic,
        dispersion_toxic_output_config_count= 1,
        end_point_concentration=0.0
        )                                   
        
    # Run the calculation
    print('Running user_defined_source_linked_run_calculation...')
    resultCode = user_defined_source_linked_run_calculation.run()

    # Print any messages.
    if len(user_defined_source_linked_run_calculation.messages) > 0:
        print('Messages:')
        for message in user_defined_source_linked_run_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        print(f'SUCCESS: user_defined_source_linked_run_calculation ({user_defined_source_linked_run_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED user_defined_source_linked_run_calculation with result code {resultCode}'
    if resultCode == ResultCode.SUCCESS:
        if (abs(user_defined_source_linked_run_calculation.jet_fire_flame_result.flame_length -1.20062703145107)/1.20062703145107 > 1e-3):
            assert False,f'Regression failed with user_defined_source_linked_run_calculation.jet_fire_flame_result.flame_length = {user_defined_source_linked_run_calculation.jet_fire_flame_result.flame_length}'
        if (abs(user_defined_source_linked_run_calculation.pool_fire_flame_result.flame_diameter -110.98406982421875)/110.98406982421875 > 1e-3):
            assert False,f'Regression failed with user_defined_source_linked_run_calculation.pool_fire_flame_result.flame_diameter = {user_defined_source_linked_run_calculation.pool_fire_flame_result.flame_diameter}'
        if (len(user_defined_source_linked_run_calculation.flam_conc_contour_points) != 845):
            assert False,f'Regression failed with len(user_defined_source_linked_run_calculation.flam_conc_contour_points) = {len(user_defined_source_linked_run_calculation.flam_conc_contour_points)}'
        if (len(user_defined_source_linked_run_calculation.toxic_conc_contour_points) != 623):
            assert False,f'Regression failed with len(user_defined_source_linked_run_calculation.toxic_conc_contour_points) = {len(user_defined_source_linked_run_calculation.toxic_conc_contour_points)}'
        if (abs(user_defined_source_linked_run_calculation.area_footprint_flam_conc[0] -58.403489642509236)/58.403489642509236 > 1e-3):
            assert False,f'Regression failed with user_defined_source_linked_run_calculation.area_footprint_flam_conc[0] = {user_defined_source_linked_run_calculation.area_footprint_flam_conc[0]}'
        if (abs(user_defined_source_linked_run_calculation.area_footprint_toxic_conc[0] -  246.68210076602227)/ 246.68210076602227 > 1e-3):
            assert False,f'Regression failed with user_defined_source_linked_run_calculation.area_footprint_toxic_conc[0] = {user_defined_source_linked_run_calculation.area_footprint_toxic_conc[0]}'
        if (abs(user_defined_source_linked_run_calculation.area_contour_jet[0] -7.049885685309768)/7.049885685309768 > 1e-3):
            assert False,f'Regression failed with user_defined_source_linked_run_calculation.area_contour_jet[0] = {user_defined_source_linked_run_calculation.area_contour_jet[0]}'
        if (abs(user_defined_source_linked_run_calculation.area_contour_pool[0] -58892.18880393686 )/58892.18880393686 >1e-3):
            assert False,f'Regression failed with user_defined_source_linked_run_calculation.area_contour_pool[0] = {user_defined_source_linked_run_calculation.area_contour_pool[0]}'
        if (abs(user_defined_source_linked_run_calculation.explosion_overpressure_results[0].exploded_mass -0.4674426254901133)/0.4674426254901133 > 1e-3):
            assert False,f'Regression failed with user_defined_source_linked_run_calculation.explosion_overpressure_results[0].exploded_mass = {user_defined_source_linked_run_calculation.explosion_overpressure_results[0].exploded_mass}'
        if (abs(user_defined_source_linked_run_calculation.explosion_overpressure_results[0].maximum_distance - 53.57915999004202)/53.57915999004202 > 1e-3):
            assert False,f'Regression failed with user_defined_source_linked_run_calculation.explosion_overpressure_results[0].maximum_distance = {user_defined_source_linked_run_calculation.explosion_overpressure_results[0].maximum_distance}'
        print(f'Flame lenght = {user_defined_source_linked_run_calculation.jet_fire_flame_result.flame_length}')
        print(f'Flame diameter = {user_defined_source_linked_run_calculation.pool_fire_flame_result.flame_diameter}')
        print(f'Length of the dispersion flammable contour array = {len(user_defined_source_linked_run_calculation.flam_conc_contour_points)}')
        print(f'Length of the dispersion toxic contour array = {len(user_defined_source_linked_run_calculation.toxic_conc_contour_points)}')
        print(f'Area of the flammable cloud = {user_defined_source_linked_run_calculation.area_footprint_flam_conc[0]}')
        print(f'Area of the toxic cloud = {user_defined_source_linked_run_calculation.area_footprint_toxic_conc[0]}')
        print(f'Area of the jet fire = {user_defined_source_linked_run_calculation.area_contour_jet[0]}')
        print(f'Area of the pool = {user_defined_source_linked_run_calculation.area_contour_pool[0]}')
        print(f'Flammable mass = {user_defined_source_linked_run_calculation.explosion_overpressure_results[0].exploded_mass}')
        print(f'Explosion maximum distance = {user_defined_source_linked_run_calculation.explosion_overpressure_results[0].maximum_distance}')
        print(f'SUCCESS: user_defined_source_linked_run_calculation ({user_defined_source_linked_run_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED user_defined_source_linked_run_calculation with result code {resultCode}'