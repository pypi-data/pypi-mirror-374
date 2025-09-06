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
from pypws.entities import Material, MaterialComponent, Substrate, Weather, DischargeParameters, FlammableParameters, ExplosionParameters, ExplosionConfinedVolume, DispersionParameters, DispersionOutputConfig, FlammableOutputConfig, ExplosionOutputConfig
from pypws.enums import AtmosphericStabilityClass, WindProfileFlag, SpecialConcentration
from pypws.enums import ResultCode


def test_case_162():

    material = Material("METHANE+ETHANE", [MaterialComponent("METHANE", 0.9), MaterialComponent("ETHANE", 0.1)], component_count = 2)


    # Create a load mass inventory vessel for line rupture scenario calculation using the material and state.
    load_mass_inventory_vessel_for_line_rupture_scenario_calculation = LoadMassInventoryVesselForLineRuptureScenarioCalculation(material = material, temperature = 250, pressure = float(11e5), mass = float(1e5), pipe_length = 10.0, pipe_diameter = 0.5, release_elevation = 100.0, release_angle = 0.0)

    # Run the calculation
    print('Running load_mass_inventory_vessel_for_line_rupture_scenario_calculation...')
    resultCode = load_mass_inventory_vessel_for_line_rupture_scenario_calculation.run()

    # Print any messages.
    if len(load_mass_inventory_vessel_for_line_rupture_scenario_calculation.messages) > 0:
        print('Messages:')
        for message in load_mass_inventory_vessel_for_line_rupture_scenario_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (abs((load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel.diameter-27.049130317992706)/27.049130317992706)>1e-3):
            assert False,f'Regression failed with load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel.diameter = {load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel.diameter}'
        if (abs((load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel.location.z-(86.47543484100365))/(86.47543484100365))>1e-3):
            assert False,f'Regression failed with load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel.location.z = {load_mass_inventory_vessel_for_line_rupture_scenario_calculation.vessel.location.z}'
        if (abs((load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture.pipe_diameter-0.5)/0.5)>1e-3):
            assert False,f'Regression failed with load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture.pipe_diameter = {load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture.pipe_diameter}'
        if (abs((load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture.pipe_height_fraction-0.5)/0.5)>1e-3):
            assert False,f'Regression failed with load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture.pipe_height_fraction = {load_mass_inventory_vessel_for_line_rupture_scenario_calculation.line_rupture.pipe_height_fraction}'
        print(f'SUCCESS: load_mass_inventory_vessel_for_line_rupture_scenario_calculation ({load_mass_inventory_vessel_for_line_rupture_scenario_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED load_mass_inventory_vessel_for_line_rupture_scenario_calculation with result code {resultCode}'

    # Define the weather conditions
    weather = Weather( wind_speed = 1.5, stability_class = AtmosphericStabilityClass.STABILITY_F, wind_profile_flag = WindProfileFlag.LOGARITHMIC_PROFILE)

    # Define the substrate
    substrate = Substrate()

    # Define the dispersion parameters
    dispersion_parameters = [DispersionParameters(averaging_time = 18.75, lfl_fraction_to_stop=0.2), DispersionParameters(averaging_time = 18.75)]

    # Define the dispersion output configuration
    dispersion_output_configs_flammable = [DispersionOutputConfig(special_concentration = SpecialConcentration.LFL_FRACTION, elevation = 100.0, lfl_fraction_value=0.2)]
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
        if (abs(vessel_line_rupture_linked_run_calculation.discharge_record.mass_flow - 369.13836776138595)/369.13836776138595 > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.discharge_record.mass_flow = {vessel_line_rupture_linked_run_calculation.discharge_record.mass_flow}'
        if (abs(vessel_line_rupture_linked_run_calculation.jet_fire_flame_result.flame_length - 132.810385487078)/132.810385487078 > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.jet_fire_flame_result.flame_length = {vessel_line_rupture_linked_run_calculation.jet_fire_flame_result.flame_length}'
        if (vessel_line_rupture_linked_run_calculation.pool_fire_flame_result.flame_diameter != 0.0):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.pool_fire_flame_result.flame_diameter = {vessel_line_rupture_linked_run_calculation.pool_fire_flame_result.flame_diameter}'
        if (len(vessel_line_rupture_linked_run_calculation.flam_conc_contour_points) != 597):
            assert False,f'Regression failed with len(vessel_line_rupture_linked_run_calculation.flam_conc_contour_points) = {len(vessel_line_rupture_linked_run_calculation.flam_conc_contour_points)}'
        if (len(vessel_line_rupture_linked_run_calculation.toxic_conc_contour_points) != 873):
            assert False,f'Regression failed with len(vessel_line_rupture_linked_run_calculation.toxic_conc_contour_points) = {len(vessel_line_rupture_linked_run_calculation.toxic_conc_contour_points)}'
        if (abs(vessel_line_rupture_linked_run_calculation.area_footprint_flam_conc[0] -16798.58475657922)/16798.58475657922 > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.area_footprint_flam_conc[0] = {vessel_line_rupture_linked_run_calculation.area_footprint_flam_conc[0]}'
        if (abs(vessel_line_rupture_linked_run_calculation.area_footprint_toxic_conc[0] - 21559290.626672193)/21559290.626672193 > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.area_footprint_toxic_conc[0] = {vessel_line_rupture_linked_run_calculation.area_footprint_toxic_conc[0]}'
        if (abs(vessel_line_rupture_linked_run_calculation.area_contour_jet[0] - 57212.96926113445)/57212.96926113445 > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.area_contour_jet[0] = {vessel_line_rupture_linked_run_calculation.area_contour_jet[0]}'
        if (vessel_line_rupture_linked_run_calculation.area_contour_pool[0] !=0.0):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.area_contour_pool[0] = {vessel_line_rupture_linked_run_calculation.area_contour_pool[0]}'
        if (abs(vessel_line_rupture_linked_run_calculation.explosion_overpressure_results[0].exploded_mass - 411.4357378379431)/411.4357378379431 > 1e-3):
            assert False,f'Regression failed with vessel_line_rupture_linked_run_calculation.explosion_overpressure_results[0].exploded_mass = {vessel_line_rupture_linked_run_calculation.explosion_overpressure_results[0].exploded_mass}'
        if (abs(vessel_line_rupture_linked_run_calculation.explosion_overpressure_results[0].maximum_distance - 593.064103906056)/593.064103906056 > 1e-3):
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