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

from pypws.calculations import LoadMassInventoryVesselForReliefValveScenarioCalculation, VesselReliefValveLinkedRunCalculation
from pypws.entities import Material, MaterialComponent, Weather, Substrate, DispersionParameters, DispersionOutputConfig, FlammableParameters, FlammableOutputConfig, ExplosionParameters, ExplosionOutputConfig, ExplosionConfinedVolume, DischargeParameters
from pypws.enums import ResultCode, AtmosphericStabilityClass, WindProfileFlag, SpecialConcentration


def test_case_168():

	material = Material("HYDROGEN", [MaterialComponent("HYDROGEN", 1.0)], component_count = 1)


	# Create a load mass inventory vessel for relief valve scenario calculation using the material.
	load_mass_inventory_vessel_for_relief_valve_scenario_calculation = LoadMassInventoryVesselForReliefValveScenarioCalculation(material = material, temperature = 250, pressure = float(7e5), mass = float(9876), pipe_length = 33.0, pipe_diameter = 0.1, constriction_size = 0.05, release_elevation = 1.0, release_angle = 1.1)

	# Run the calculation
	print('Running load_mass_inventory_vessel_for_relief_valve_scenario_calculation...')
	resultCode = load_mass_inventory_vessel_for_relief_valve_scenario_calculation.run()

	# Print any messages.
	if len(load_mass_inventory_vessel_for_relief_valve_scenario_calculation.messages) > 0:
		print('Messages:')
		for message in load_mass_inventory_vessel_for_relief_valve_scenario_calculation.messages:
			print(message)

	if resultCode == ResultCode.SUCCESS:
		if (abs((load_mass_inventory_vessel_for_relief_valve_scenario_calculation.vessel.diameter- 30.344485738881644)/ 30.344485738881644)>1e-3):
			assert False, f'Regression failed with load_mass_inventory_vessel_for_relief_valve_scenario_calculation.vessel.diameter = {load_mass_inventory_vessel_for_relief_valve_scenario_calculation.vessel.diameter}'
		if (abs((load_mass_inventory_vessel_for_relief_valve_scenario_calculation.vessel.location.z-(-14.172242869440822))/(-14.172242869440822))>1e-3):
			assert False, f'Regression failed load_mass_inventory_vessel_for_relief_valve_scenario_calculation.vessel.location.z = {load_mass_inventory_vessel_for_relief_valve_scenario_calculation.vessel.location.z}'
		if (abs((load_mass_inventory_vessel_for_relief_valve_scenario_calculation.relief_valve.pipe_diameter-0.1)/0.1)>1e-3):
			assert False, f'Regression failed with load_mass_inventory_vessel_for_relief_valve_scenario_calculation.relief_valve.pipe_diameter = {load_mass_inventory_vessel_for_relief_valve_scenario_calculation.relief_valve.pipe_diameter}'
		if (abs((load_mass_inventory_vessel_for_relief_valve_scenario_calculation.relief_valve.pipe_height_fraction-0.5)/0.5)>1e-3):
			assert False, f'Regression failed with load_mass_inventory_vessel_for_relief_valve_scenario_calculation.relief_valve.pipe_height_fraction = {load_mass_inventory_vessel_for_relief_valve_scenario_calculation.relief_valve.pipe_height_fraction}'
		print(f'SUCCESS: load_mass_inventory_vessel_for_relief_valve_scenario_calculation ({load_mass_inventory_vessel_for_relief_valve_scenario_calculation.calculation_elapsed_time}ms)')
	else:
		assert False, f'FAILED load_mass_inventory_vessel_for_relief_valve_scenario_calculation with result code {resultCode}'

	# Define the weather conditions
	weather = Weather( wind_speed = 10.0, stability_class = AtmosphericStabilityClass.STABILITY_A, wind_profile_flag = WindProfileFlag.LOGARITHMIC_PROFILE)

	# Define the substrate
	substrate = Substrate()

	# Define the dispersion parameters
	dispersion_parameters = [DispersionParameters(averaging_time = 18.75), DispersionParameters(averaging_time =18.75)]

	# Define the dispersion output configuration
	dispersion_output_configs_flammable = [DispersionOutputConfig(special_concentration = SpecialConcentration.LFL_FRACTION,  elevation = 0.0)]
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
	vessel_relief_valve_linked_run_calculation = VesselReliefValveLinkedRunCalculation(
		vessel = load_mass_inventory_vessel_for_relief_valve_scenario_calculation.vessel,
		relief_valve = load_mass_inventory_vessel_for_relief_valve_scenario_calculation.relief_valve,
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
	print('Running vessel_relief_valve_linked_run_calculation...')
	resultCode = vessel_relief_valve_linked_run_calculation.run()

	# Print any messages.
	if len(vessel_relief_valve_linked_run_calculation.messages) > 0:
		print('Messages:')
		for message in vessel_relief_valve_linked_run_calculation.messages:
			print(message)

	if resultCode == ResultCode.SUCCESS:
		if (abs(vessel_relief_valve_linked_run_calculation.discharge_record.mass_flow - 0.9443675979173782)/0.9443675979173782> 1e-3):
			assert False,f'Regression failed with vessel_relief_valve_linked_run_calculation.discharge_record.mass_flow = {vessel_relief_valve_linked_run_calculation.discharge_record.mass_flow}'
		if (abs(vessel_relief_valve_linked_run_calculation.jet_fire_flame_result.flame_length - 11.028079519540297)/11.028079519540297 > 1e-3):
			assert False,f'Regression failed with vessel_relief_valve_linked_run_calculation.jet_fire_flame_result.flame_length = {vessel_relief_valve_linked_run_calculation.jet_fire_flame_result.flame_length}'
		if (vessel_relief_valve_linked_run_calculation.pool_fire_flame_result.flame_diameter != 0.0):
			assert False,f'Regression failed with vessel_relief_valve_linked_run_calculation.pool_fire_flame_result.flame_diameter = {vessel_relief_valve_linked_run_calculation.pool_fire_flame_result.flame_diameter}'
		if (len(vessel_relief_valve_linked_run_calculation.flam_conc_contour_points) != 0):
			assert False,f'Regression failed with len(vessel_relief_valve_linked_run_calculation.flam_conc_contour_points) = {len(vessel_relief_valve_linked_run_calculation.flam_conc_contour_points)}'
		if (len(vessel_relief_valve_linked_run_calculation.toxic_conc_contour_points) != 603):
			assert False,f'Regression failed with len(vessel_relief_valve_linked_run_calculation.toxic_conc_contour_points) = {len(vessel_relief_valve_linked_run_calculation.toxic_conc_contour_points)}'
		if (vessel_relief_valve_linked_run_calculation.area_footprint_flam_conc[0]!= 0.0):
			assert False,f'Regression failed with vessel_relief_valve_linked_run_calculation.area_footprint_flam_conc[0] = {vessel_relief_valve_linked_run_calculation.area_footprint_flam_conc[0]}'
		if (abs(vessel_relief_valve_linked_run_calculation.area_footprint_toxic_conc[0] -33801.6456631375)/33801.6456631375 > 1e-3):
			assert False,f'Regression failed with vessel_relief_valve_linked_run_calculation.area_footprint_toxic_conc[0] = {vessel_relief_valve_linked_run_calculation.area_footprint_toxic_conc[0]}'
		if (abs(vessel_relief_valve_linked_run_calculation.area_contour_jet[0]-  396.48256520388253)/ 396.48256520388253 > 1e-3):
			assert False,f'Regression failed with vessel_relief_valve_linked_run_calculation.area_contour_jet[0] = {vessel_relief_valve_linked_run_calculation.area_contour_jet[0]}'
		if (vessel_relief_valve_linked_run_calculation.area_contour_pool[0] != 0.0):
			assert False,f'Regression failed with vessel_relief_valve_linked_run_calculation.area_contour_pool[0] = {vessel_relief_valve_linked_run_calculation.area_contour_pool[0]}'
		if (abs(vessel_relief_valve_linked_run_calculation.explosion_overpressure_results[0].exploded_mass-0.20630565247270963)/0.20630565247270963 > 1e-3):	
			assert False,f'Regression failed with vessel_relief_valve_linked_run_calculation.explosion_overpressure_results[0].exploded_mass = {vessel_relief_valve_linked_run_calculation.explosion_overpressure_results[0].exploded_mass}'
		if (abs(vessel_relief_valve_linked_run_calculation.explosion_overpressure_results[0].maximum_distance - 45.518593970444364)/45.518593970444364 > 1e-3):
			assert False,f'Regression failed with vessel_relief_valve_linked_run_calculation.explosion_overpressure_results[0].maximum_distance = {vessel_relief_valve_linked_run_calculation.explosion_overpressure_results[0].maximum_distance}'
		print(f'Mass flow ={vessel_relief_valve_linked_run_calculation.discharge_record.mass_flow}')
		print(f'Flame lenght = {vessel_relief_valve_linked_run_calculation.jet_fire_flame_result.flame_length}')
		print(f'Flame diameter = {vessel_relief_valve_linked_run_calculation.pool_fire_flame_result.flame_diameter}')
		print(f'Length of the dispersion flammable contour array = {len(vessel_relief_valve_linked_run_calculation.flam_conc_contour_points)}')
		print(f'Length of the dispersion toxic contour array = {len(vessel_relief_valve_linked_run_calculation.toxic_conc_contour_points)}')
		print(f'Area of the flammable cloud = {vessel_relief_valve_linked_run_calculation.area_footprint_flam_conc[0]}')
		print(f'Area of the toxic cloud = {vessel_relief_valve_linked_run_calculation.area_footprint_toxic_conc[0]}')
		print(f'Area of the jet fire = {vessel_relief_valve_linked_run_calculation.area_contour_jet[0]}')
		print(f'Area of the pool = {vessel_relief_valve_linked_run_calculation.area_contour_pool[0]}')
		print(f'Flammable mass = {vessel_relief_valve_linked_run_calculation.explosion_overpressure_results[0].exploded_mass}')
		print(f'Explosion maximum distance = {vessel_relief_valve_linked_run_calculation.explosion_overpressure_results[0].maximum_distance}')
		print(f'SUCCESS: vessel_relief_valve_linked_run_calculation ({vessel_relief_valve_linked_run_calculation.calculation_elapsed_time}ms)')
	else:
		assert False, f'FAILED vessel_relief_valve_linked_run_calculation with result code {resultCode}'		