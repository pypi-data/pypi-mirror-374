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
    JetFireCalculation,
    RadiationContourCalculation,
    VesselLeakCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    Bund,
    DischargeParameters,
    FlammableOutputConfig,
    FlammableParameters,
    Leak,
    LineRupture,
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
    ContourType
)


def test_case_52():
    """Radiation contour calculation test case with the following properties:
    material_name = 'N-BUTANE'
    state_temperature = 220.0
    state_pressure = 1.0E+06
    vessel_shape = VesselShape.VESSEL_SPHERE
    vessel_diameter = 3.0
    leak_hole_diameter = 0.1
    time_varying_option = TimeVaryingOption.INITIAL_RATE
    leak_hole_height_fraction = 0.5
    liquid_fill_fraction_by_volume = 0.5
    wind_speed = 2.0
    stability_class = AtmosphericStabilityClass.STABILITY_F
    time_of_interest = 2600.0
    radiation_resolution = Resolution.HIGH
    """

    # Set the case properties.
    material_name = 'N-BUTANE'
    state_temperature = 220.0
    state_pressure = 1.0E+06
    vessel_shape = VesselShape.VESSEL_SPHERE
    vessel_diameter = 3.0
    leak_hole_diameter = 0.1
    time_varying_option = TimeVaryingOption.INITIAL_RATE
    leak_hole_height_fraction = 0.5
    liquid_fill_fraction_by_volume = 0.5
    wind_speed = 2.0
    stability_class = AtmosphericStabilityClass.STABILITY_F
    time_of_interest = 2600.0
    radiation_resolution = Resolution.HIGH

    # Define the initial state of the vessel.
    state = State(temperature = state_temperature, pressure = state_pressure, liquid_fraction = 0.0)

    # Define the material contained by the vessel.
    material = Material(material_name, [MaterialComponent(material_name, 1.0)])

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
    flammable_output_config = FlammableOutputConfig(position = LocalPosition(0.0, 0.0, 2.0), transect = Transect(transect_start_point = LocalPosition(), transect_end_point = LocalPosition()), radiation_resolution= radiation_resolution, contour_type=ContourType.FOOTPRINT)


    # Create a radiation contour calculation using the flame result, flame records, weather, flammable parameters, and flammable output configurations.
    radiation_contour_calculation = RadiationContourCalculation(flame_result=jet_fire_calculation.flame_result, 
                                                                flame_records=jet_fire_calculation.flame_records, 
                                                                flame_record_count=len(jet_fire_calculation.flame_records), 
                                                                weather=weather, 
                                                                flammable_parameters=jet_fire_calculation.flammable_parameters, 
                                                                flammable_output_config=flammable_output_config)

    # Run the radiation contour calculation.
    print('Running radiation_contour_calculation...')
    result_code = radiation_contour_calculation.run()

    # Print any messages.
    print(result_code)
    if len(radiation_contour_calculation.messages) > 0:
        print('Messages:')
        for message in radiation_contour_calculation.messages:
            print(message)

    if result_code == ResultCode.SUCCESS:
        if (len(radiation_contour_calculation.contour_points) != 510):
            assert False,f'Regression failed with len(radiation_contour_calculation.contour_points) = {len(radiation_contour_calculation.contour_points)}'
        if (abs((radiation_contour_calculation.contour_points[len(radiation_contour_calculation.contour_points)-2].x-31.90799616657131)/31.90799616657131)>1e-3):
            assert False,f'Regression failed with radiation_contour_calculation.contour_points[len(radiation_contour_calculation.contour_points)-2].x = {radiation_contour_calculation.contour_points[len(radiation_contour_calculation.contour_points)-2].x}'
        if (abs((radiation_contour_calculation.flame_result.flame_length- 138.4978616734956)/ 138.4978616734956)>1e-3):
            assert False,f'Regression failed with radiation_contour_calculation.flame_result.flame_length = {radiation_contour_calculation.flame_result.flame_length}'
        print(f'SUCCESS: radiation_contour_calculation ({radiation_contour_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED radiation_contour_calculation with result code {result_code}'
        




