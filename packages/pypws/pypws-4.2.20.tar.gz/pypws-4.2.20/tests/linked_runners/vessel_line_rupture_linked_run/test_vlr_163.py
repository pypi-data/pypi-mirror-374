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

from pypws.calculations import LoadMassInventoryVesselForLineRuptureScenarioCalculation, VesselLineRuptureLinkedRunCalculation
from pypws.entities import Material, MaterialComponent, Substrate, Weather, DispersionParameters, DispersionOutputConfig, FlammableParameters, FlammableOutputConfig, ExplosionParameters, ExplosionOutputConfig, ExplosionConfinedVolume, DischargeParameters, Bund
from pypws.enums import ResultCode, AtmosphericStabilityClass, WindProfileFlag, SpecialConcentration


def test_case_163():

    material = Material("N-HEXANE", [MaterialComponent("N-HEXANE", 1.0)], component_count = 1)


    # Create a load mass inventory vessel for line rupture scenario calculation using the material.
    load_mass_inventory_vessel_for_line_rupture_scenario_calculation = LoadMassInventoryVesselForLineRuptureScenarioCalculation(material = material, temperature = 250, pressure = float(7e5), mass = float(9876), pipe_length = 7.5, pipe_diameter = 0.1, release_elevation = 0.0, release_angle = 0.0)

    # Run the calculation
    print('Running load_mass_inventory_vessel_for_line_rupture_scenario_calculation...')
    resultCode = load_mass_inventory_vessel_for_line_rupture_scenario_calculation.run()

    # Print any messages.
    if len(load_mass_inventory_vessel_for_line_rupture_scenario_calculation.messages) > 0:
        print('Messages:')
        for message in load_mass_inventory_vessel_for_line_rupture_scenario_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (abs((load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel.diameter-3.0323298714998153)/3.0323298714998153)>1e-3):
            assert False,f'Regression failed with load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel.diameter = {load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel.diameter}'
        if (abs((load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel.location.z-(-2.7170445294165657))/(-2.7170445294165657))>1e-3):
            assert False,f'Regression failed with load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel.location.z = {load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel.location.z}'
        if (abs((load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture.pipe_diameter-0.1)/0.1)>1e-3):
            assert False,f'Regression failed with load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture.pipe_diameter = {load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture.pipe_diameter}'
        if (abs((load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture.pipe_height_fraction-0.8960253813259087)/0.8960253813259087)>1e-3):
            assert False,f'Regression failed with load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture.pipe_height_fraction = {load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture.pipe_height_fraction}'
        print(f'SUCCESS: load_mass_inventory_vessel_for_line_rupture_scenario_calculation ({load_mass_inventory_vessel_for_line_rupture_scenario_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED load_mass_inventory_vessel_for_line_rupture_scenario_calculation with result code {resultCode}'

    # Define the weather conditions
    weather = Weather( wind_speed = 2.0, stability_class = AtmosphericStabilityClass.STABILITY_CD, wind_profile_flag = WindProfileFlag.LOGARITHMIC_PROFILE)

    # Define the substrate
    substrate = Substrate(bund = Bund(specify_bund=True, bund_height = 2.0, bund_diameter = 20.0))

    # Define the dispersion parameters
    dispersion_parameters = [DispersionParameters(averaging_time = 18.75, lfl_fraction_to_stop=0.15), DispersionParameters(averaging_time = 18.75)]

    # Define the dispersion output configuration
    dispersion_output_configs_flammable = [DispersionOutputConfig(special_concentration = SpecialConcentration.LFL_FRACTION, lfl_fraction_value= 0.15,  elevation = 0.0)]
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

    # 
    vessel_line_rupture_linked_run_calculation = VesselLineRuptureLinkedRunCalculation(
        vessel = load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel,
        line_rupture = load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture,
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
    print('Running vessel_line_rupture_linked_run_calculation...')
    resultCode = vessel_line_rupture_linked_run_calculation.run()

    # Print any messages.
    if len(vessel_line_rupture_linked_run_calculation.messages) > 0:
        print('Messages:')
        for message in vessel_line_rupture_linked_run_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (abs(vessel_line_rupture_linked_run_calculation.discharge_record.mass_flow - 131.73664600034286)/131.73664600034286 > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.discharge_record.mass_flow = {vessel_line_rupture_linked_run_calculation.discharge_record.mass_flow}'
        if (vessel_line_rupture_linked_run_calculation.jet_fire_flame_result.flame_length != 0.0):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.jet_fire_flame_result.flame_length = {vessel_line_rupture_linked_run_calculation.jet_fire_flame_result.flame_length}'
        if (abs(vessel_line_rupture_linked_run_calculation.pool_fire_flame_result.flame_diameter - 20.00299644470215)/20.00299644470215 > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.pool_fire_flame_result.flame_diameter = {vessel_line_rupture_linked_run_calculation.pool_fire_flame_result.flame_diameter}'
        if (len(vessel_line_rupture_linked_run_calculation.flam_conc_contour_points) != 563):
            assert False,f'Regression failed with len(vessel_line_rupture_linked_run_calculation.flam_conc_contour_points) = {len(vessel_line_rupture_linked_run_calculation.flam_conc_contour_points)}'
        if (len(vessel_line_rupture_linked_run_calculation.toxic_conc_contour_points) != 623):
            assert False,f'Regression failed with len(vessel_line_rupture_linked_run_calculation.toxic_conc_contour_points) = {len(vessel_line_rupture_linked_run_calculation.toxic_conc_contour_points)}'
        if (abs(vessel_line_rupture_linked_run_calculation.area_footprint_flam_conc[0]- 585.0061568126835)/ 585.0061568126835 > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.area_footprint_flam_conc[0] = {vessel_line_rupture_linked_run_calculation.area_footprint_flam_conc[0]}'
        if (abs(vessel_line_rupture_linked_run_calculation.area_footprint_toxic_conc[0] -12934.3464614692)/12934.3464614692 > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.area_footprint_toxic_conc[0] = {vessel_line_rupture_linked_run_calculation.area_footprint_toxic_conc[0]}'
        if (vessel_line_rupture_linked_run_calculation.area_contour_jet[0]!= 0.0):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.area_contour_jet[0] = {vessel_line_rupture_linked_run_calculation.area_contour_jet[0]}'
        if (abs(vessel_line_rupture_linked_run_calculation.area_contour_pool[0] - 4498.14606654948)/4498.14606654948 > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.area_contour_pool[0] = {vessel_line_rupture_linked_run_calculation.area_contour_pool[0]}'
        if (vessel_line_rupture_linked_run_calculation.explosion_overpressure_results[0].exploded_mass!= 0.0):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.explosion_overpressure_results[0].exploded_mass = {vessel_line_rupture_linked_run_calculation.explosion_overpressure_results[0].exploded_mass}'
        if (vessel_line_rupture_linked_run_calculation.explosion_overpressure_results[0].maximum_distance != 0.0):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.explosion_overpressure_results[0].maximum_distance = {vessel_line_rupture_linked_run_calculation.explosion_overpressure_results[0].maximum_distance}'
        print(f'Mass flow ={vessel_line_rupture_linked_run_calculation.discharge_record.mass_flow}')
        print(f'Flame lenght = {vessel_line_rupture_linked_run_calculation.jet_fire_flame_result.flame_length}')
        print(f'Flame diameter = {vessel_line_rupture_linked_run_calculation.pool_fire_flame_result.flame_diameter}')
        print(f'Length of the dispersion flammable contour array = {len(vessel_line_rupture_linked_run_calculation.flam_conc_contour_points)}')
        print(f'Length of the dispersion toxic contour array = {len(vessel_line_rupture_linked_run_calculation.toxic_conc_contour_points)}')
        print(f'Area of the flammable cloud = {vessel_line_rupture_linked_run_calculation.area_footprint_flam_conc[0]}')
        print(f'Area of the toxic cloud = {vessel_line_rupture_linked_run_calculation.area_footprint_toxic_conc[0]}')
        print(f'Area of the jet fire = {vessel_line_rupture_linked_run_calculation.area_contour_jet[0]}')
        print(f'Area of the pool = {vessel_line_rupture_linked_run_calculation.area_contour_pool[0]}')
        print(f'Flammable mass = {vessel_line_rupture_linked_run_calculation.explosion_overpressure_results[0].exploded_mass}')
        print(f'Explosion maximum distance = {vessel_line_rupture_linked_run_calculation.explosion_overpressure_results[0].maximum_distance}')
        print(f'SUCCESS: vessel_line_rupture_linked_run_calculation ({vessel_line_rupture_linked_run_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED vessel_line_rupture_linked_run_calculation with result code {resultCode}'		
