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

from pypws.calculations import LoadMassInventoryVesselForLeakScenarioCalculation, VesselLeakLinkedRunCalculation
from pypws.entities import Material, MaterialComponent, Weather, Substrate, DischargeParameters, FlammableParameters, DispersionParameters, FlammableParameters, ExplosionParameters, ExplosionOutputConfig, ExplosionConfinedVolume, FlammableOutputConfig, DispersionOutputConfig, ExplosionConfinedVolume
from pypws.enums import ResultCode, AtmosphericStabilityClass, SpecialConcentration, WindProfileFlag, MixtureModelling


def test_vlr_158():
	
    material = Material("PROPANE+N-BUTANE+N-PENTANE", [MaterialComponent("PROPANE", 0.1), MaterialComponent("N-BUTANE", 0.3), MaterialComponent("N-PENTANE", 0.6)], component_count = 3)


    # Create a load mass inventory vessel for leak scenario calculation using the material.
    load_mass_inventory_vessel_for_leak_scenario_calculation = LoadMassInventoryVesselForLeakScenarioCalculation(material = material, temperature = 250, pressure = float(6E5), mass = float(1e4), hole_size=0.08, release_elevation = 1.0, release_angle = 0.0)

    # Run the calculation
    print('Running load_mass_inventory_vessel_for_leak_scenario_calculation...')
    resultCode = load_mass_inventory_vessel_for_leak_scenario_calculation.run()

    # Print any messages.
    if len(load_mass_inventory_vessel_for_leak_scenario_calculation.messages) > 0:
        print('Messages:')
        for message in load_mass_inventory_vessel_for_leak_scenario_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        print(f'SUCCESS: load_mass_inventory_vessel_for_leak_scenario_calculation ({load_mass_inventory_vessel_for_leak_scenario_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED load_mass_inventory_vessel_for_leak_scenario_calculation with result code {resultCode}'

    # Define the weather conditions
    weather = Weather( wind_speed = 5.0, stability_class = AtmosphericStabilityClass.STABILITY_B, wind_profile_flag = WindProfileFlag.LOGARITHMIC_PROFILE)

    # Define the substrate
    substrate = Substrate()

    # Define the dispersion parameters
    dispersion_parameters = [DispersionParameters(averaging_time = 18.75), DispersionParameters(averaging_time = 18.75)]

    # Define the dispersion output configuration
    dispersion_output_configs_flammable = [DispersionOutputConfig(special_concentration = SpecialConcentration.LFL_FRACTION, elevation = 0.0)]
    dispersion_output_configs_toxic = [DispersionOutputConfig(special_concentration = SpecialConcentration.NOT_DEFINED, concentration = 5e-5, elevation = 0.0)]

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

    vessel = load_mass_inventory_vessel_for_leak_scenario_calculation.vessel
    vessel.state.mixture_modelling = MixtureModelling.MC_MULTIPLE_AEROSOL
    # 
    vessel_leak_linked_run_calculation = VesselLeakLinkedRunCalculation(
        vessel = vessel,
        leak = load_mass_inventory_vessel_for_leak_scenario_calculation.leak,
        discharge_parameters = DischargeParameters(),
        substrate = substrate,
        weather = weather,
        dispersion_parameters = dispersion_parameters,
        dispersion_parameter_count = len(dispersion_parameters),
        end_point_concentration = 0.0,
        flammable_parameters = flammable_parameters,
        explosion_parameters = explosion_parameters,
        dispersion_flam_output_configs = dispersion_output_configs_flammable,
        dispersion_flam_output_config_count = len(dispersion_output_configs_flammable),
        dispersion_toxic_output_configs = dispersion_output_configs_toxic,
        dispersion_toxic_output_config_count = len(dispersion_output_configs_toxic),
        flammable_output_configs = flammable_output_configs,
        flammable_output_config_count = len(flammable_output_configs),
        explosion_output_configs = explosion_output_configs,
        explosion_output_config_count = len(explosion_output_configs),
        explosion_confined_volumes = explosion_confined_volumes,
        explosion_confined_volume_count = len(explosion_confined_volumes)
    )

    # Run the calculation
    print('Running vessel_leak_linked_run_calculation...')
    resultCode = vessel_leak_linked_run_calculation.run()

    # Print any messages.
    if len(vessel_leak_linked_run_calculation.messages) > 0:
        print('Messages:')
        for message in vessel_leak_linked_run_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (abs(vessel_leak_linked_run_calculation.discharge_record.mass_flow - 79.92636564283663)/79.92636564283663 > 1e-3):
            assert False,f'Regression failed with vessel_leak_linked_run_calculation.discharge_record.mass_flow = {vessel_leak_linked_run_calculation.discharge_record.mass_flow}'
        if (abs(vessel_leak_linked_run_calculation.jet_fire_flame_result.flame_length - 77.05440102800145)/77.05440102800145 > 1e-3):
            assert False,f'Regression failed with vessel_leak_linked_run_calculation.jet_fire_flame_result.flame_length = {vessel_leak_linked_run_calculation.jet_fire_flame_result.flame_length}'
        if (abs(vessel_leak_linked_run_calculation.pool_fire_flame_result.flame_diameter - 41.782142639160156)/41.782142639160156 > 1e-3):
            assert False,f'Regression failed with vessel_leak_linked_run_calculation.pool_fire_flame_result.flame_diameter = {vessel_leak_linked_run_calculation.pool_fire_flame_result.flame_diameter}'
        if (len(vessel_leak_linked_run_calculation.flam_conc_contour_points) != 601):
            assert False,f'Regression failed with len(vessel_leak_linked_run_calculation.flam_conc_contour_points) = {len(vessel_leak_linked_run_calculation.flam_conc_contour_points)}'
        if (len(vessel_leak_linked_run_calculation.toxic_conc_contour_points) != 693):
            assert False,f'Regression failed with len(vessel_leak_linked_run_calculation.toxic_conc_contour_points) = {len(vessel_leak_linked_run_calculation.toxic_conc_contour_points)}'
        if (abs(vessel_leak_linked_run_calculation.area_footprint_flam_conc[0] - 11080.56953438209)/11080.56953438209 > 1e-3):
            assert False,f'Regression failed with vessel_leak_linked_run_calculation.area_footprint_flam_conc[0] = {vessel_leak_linked_run_calculation.area_footprint_flam_conc[0]}'
        if (abs(vessel_leak_linked_run_calculation.area_footprint_toxic_conc[0] - 445160.15045601147)/445160.15045601147 > 1e-3):
            assert False,f'Regression failed with vessel_leak_linked_run_calculation.area_footprint_toxic_conc[0] = {vessel_leak_linked_run_calculation.area_footprint_toxic_conc[0]}'
        if (abs(vessel_leak_linked_run_calculation.area_contour_jet[0] - 61978.79874189871)/61978.79874189871 > 1e-3):
            assert False,f'Regression failed with vessel_leak_linked_run_calculation.area_contour_jet[0] = {vessel_leak_linked_run_calculation.area_contour_jet[0]}'
        if (abs(vessel_leak_linked_run_calculation.area_contour_pool[0] - 14778.202000753792)/14778.202000753792 > 1e-3):
            assert False,f'Regression failed with vessel_leak_linked_run_calculation.area_contour_pool[0] = {vessel_leak_linked_run_calculation.area_contour_pool[0]}'
        if (abs(vessel_leak_linked_run_calculation.explosion_overpressure_results[0].exploded_mass -  680.3354816239089)/ 680.3354816239089 > 1e-3):
            assert False,f'Regression failed with vessel_leak_linked_run_calculation.explosion_overpressure_results[0].exploded_mass = {vessel_leak_linked_run_calculation.explosion_overpressure_results[0].exploded_mass}'
        if (abs(vessel_leak_linked_run_calculation.explosion_overpressure_results[0].maximum_distance - 552.0412952025639)/552.0412952025639 > 1e-3):
            assert False,f'Regression failed with vessel_leak_linked_run_calculation.explosion_overpressure_results[0].maximum_distance = {vessel_leak_linked_run_calculation.explosion_overpressure_results[0].maximum_distance}'
        print(f'Mass flow ={vessel_leak_linked_run_calculation.discharge_record.mass_flow}')
        print(f'Flame lenght = {vessel_leak_linked_run_calculation.jet_fire_flame_result.flame_length}')
        print(f'Flame diameter = {vessel_leak_linked_run_calculation.pool_fire_flame_result.flame_diameter}')
        print(f'Length of the dispersion flammable contour array = {len(vessel_leak_linked_run_calculation.flam_conc_contour_points)}')
        print(f'Length of the dispersion toxic contour array = {len(vessel_leak_linked_run_calculation.toxic_conc_contour_points)}')
        print(f'Area of the flammable cloud = {vessel_leak_linked_run_calculation.area_footprint_flam_conc[0]}')
        print(f'Area of the toxic cloud = {vessel_leak_linked_run_calculation.area_footprint_toxic_conc[0]}')
        print(f'Area of the jet fire = {vessel_leak_linked_run_calculation.area_contour_jet[0]}')
        print(f'Area of the pool = {vessel_leak_linked_run_calculation.area_contour_pool[0]}')
        print(f'Flammable mass = {vessel_leak_linked_run_calculation.explosion_overpressure_results[0].exploded_mass}')
        print(f'Explosion maximum distance = {vessel_leak_linked_run_calculation.explosion_overpressure_results[0].maximum_distance}')
        print(f'SUCCESS: vessel_leak_linked_run_calculation ({vessel_leak_linked_run_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED vessel_leak_linked_run_calculation with result code {resultCode}'