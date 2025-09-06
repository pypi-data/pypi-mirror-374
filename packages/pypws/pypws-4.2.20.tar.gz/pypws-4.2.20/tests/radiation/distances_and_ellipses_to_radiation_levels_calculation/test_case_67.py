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


from pypws.calculations import (
    DistancesAndEllipsesToRadiationLevelsCalculation,
    JetFireCalculation,
    VesselLeakCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    DischargeParameters,
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
    Resolution,
    ResultCode,
    TimeVaryingOption,
    VesselShape,
)


def test_case_67():
    """Distances and ellipses to radiation levels calculation test case with the following properties:
    material_name = "ETHANE_METHANE_HYDROGEN"
    state_temperature = 360.0
    state_pressure = 3.0E+06
    vessel_shape = VesselShape.VESSEL_SPHERE
    vessel_diameter = 3.0
    leak_hole_diameter = 0.1
    time_varying_option = TimeVaryingOption.INITIAL_RATE
    leak_hole_height_fraction = 0.3
    liquid_fill_fraction_by_volume = 0.4
    wind_speed = 2.0
    stability_class = AtmosphericStabilityClass.STABILITY_F
    time_of_interest = 2600.0
    radiation_resolution = Resolution.EXTREME
    """

    # Set the case properties.
    material_name = "ETHANE_METHANE_HYDROGEN"
    state_temperature = 360.0
    state_pressure = 3.0E+06
    vessel_shape = VesselShape.VESSEL_SPHERE
    vessel_diameter = 3.0
    leak_hole_diameter = 0.1
    time_varying_option = TimeVaryingOption.INITIAL_RATE
    leak_hole_height_fraction = 0.3
    liquid_fill_fraction_by_volume = 0.4
    wind_speed = 2.0
    stability_class = AtmosphericStabilityClass.STABILITY_F
    time_of_interest = 2600.0
    radiation_resolution = Resolution.EXTREME

    # Define the initial state of the vessel.
    state = State(temperature = state_temperature, pressure = state_pressure, liquid_fraction = 0.0)

    # Define the material contained by the vessel.
    material = Material(material_name, [MaterialComponent("ETHANE", 0.5), MaterialComponent("METHANE", 0.3), MaterialComponent("HYDROGEN", 0.2)], component_count=3)

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
    # Values are defaulted.
    vessel = Vessel(state = vessel_state_calculation.output_state, 
                    material = vessel_state_calculation.material, 
                    vessel_conditions = vessel_state_calculation.vessel_conditions, 
                    location = LocalPosition(), 
                    diameter = vessel_diameter, 
                    shape = vessel_shape, 
                    liquid_fill_fraction_by_volume=liquid_fill_fraction_by_volume)

    # Create a leak to use in the vessel leak calculation.
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

    # Instantiate the data required by the jet fire calculation.
    weather = Weather(wind_speed = wind_speed, stability_class = stability_class)
    substrate = Substrate()
    flammable_parameters = FlammableParameters(time_of_interest = time_of_interest)

    # Create a jet fire calculation using the required input data.
    jet_fire_calculation = JetFireCalculation(vessel_leak_calculation.exit_material, 
                                            vessel_leak_calculation.discharge_records, 
                                            len(vessel_leak_calculation.discharge_records), 
                                            vessel_leak_calculation.discharge_result, 
                                            weather, 
                                            substrate, 
                                            flammable_parameters)

    # Run the jet fire calculation.
    print('Running jet_fire_calculation...')
    resultCode = jet_fire_calculation.run()

    # Print any messages.
    if len(jet_fire_calculation.messages) > 0:
        print('Messages:')
        for message in jet_fire_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        print(f'SUCCESS: jet_fire_calculation ({jet_fire_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED jet_fire_calculation with result code {resultCode}'

    # Create flammable output configurations.
    flammable_output_configs = [FlammableOutputConfig(position = LocalPosition(0.0, 0.0, 2.0), transect = Transect(transect_start_point = LocalPosition(), transect_end_point = LocalPosition()), radiation_resolution= radiation_resolution), 
                            FlammableOutputConfig(position = LocalPosition(0.0, 0.0, 2.0), transect = Transect(transect_start_point = LocalPosition(), transect_end_point = LocalPosition()), radiation_resolution= radiation_resolution), 
                            FlammableOutputConfig(position = LocalPosition(0.0, 0.0, 2.0), transect = Transect(transect_start_point = LocalPosition(), transect_end_point = LocalPosition()), radiation_resolution= radiation_resolution)]


    # Create a distances and ellipses to radiation levels calculation using the flame result, flame records, weather, flammable parameters, and flammable output configurations.
    distances_and_ellipses_to_radiation_levels_calculation = DistancesAndEllipsesToRadiationLevelsCalculation(flame_result=jet_fire_calculation.flame_result, 
                                                                flame_records=jet_fire_calculation.flame_records, 
                                                                flame_record_count=len(jet_fire_calculation.flame_records), 
                                                                weather=weather,    flammable_parameters=jet_fire_calculation.flammable_parameters, 
                                                                flammable_output_configs=flammable_output_configs,
                                                                flammable_output_config_count = len(flammable_output_configs))

    # Run the distances and ellipses to radiation levels calculation.
    print('Running distances_and_ellipses_to_radiation_levels_calculation...')
    result_code = distances_and_ellipses_to_radiation_levels_calculation.run()

    # Print any messages.
    if len(distances_and_ellipses_to_radiation_levels_calculation.messages) > 0:
        print('Messages:')
        for message in distances_and_ellipses_to_radiation_levels_calculation.messages:
            print(message)

    if result_code == ResultCode.SUCCESS:
        if (len(distances_and_ellipses_to_radiation_levels_calculation.contour_points)!= 150):
            assert False, f'Regression failed with len(distances_and_ellipses_to_radiation_levels_calculation.contour_points) = {len(distances_and_ellipses_to_radiation_levels_calculation.contour_points)}'
        if (len(distances_and_ellipses_to_radiation_levels_calculation.contour_points) > 0):    
            if (abs(distances_and_ellipses_to_radiation_levels_calculation.contour_points[len(distances_and_ellipses_to_radiation_levels_calculation.contour_points)-1].x -96.74496662598202)/96.74496662598202 > 1e-3):
                assert False, f'Regression failed with last element x of contour points = {distances_and_ellipses_to_radiation_levels_calculation.contour_points[len(distances_and_ellipses_to_radiation_levels_calculation.contour_points)-1].x}'
        if (abs(distances_and_ellipses_to_radiation_levels_calculation.areas[0]-11027.574303452657)/11027.574303452657 > 1e-3):
            assert False, f'Regression failed with distances_and_ellipses_to_radiation_levels_calculation.areas[0] = {distances_and_ellipses_to_radiation_levels_calculation.areas[0]}'
        print(f'SUCCESS: distances_and_ellipses_to_radiation_levels_calculation ({distances_and_ellipses_to_radiation_levels_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED distances_and_ellipses_to_radiation_levels_calculation with result code {result_code}'
        




