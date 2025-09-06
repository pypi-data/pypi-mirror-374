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
    DispersionCalculation,
    SideviewAtTimeCalculation,
    VesselLeakCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    DischargeParameters,
    DispersionOutputConfig,
    DispersionParameters,
    Leak,
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
    SurfaceType,
    TimeVaryingOption,
    VesselShape,
    WindProfileFlag
)


def test_case_33b():

    """
        Sideview at time calculation test case with the following properties:

        material_name = 'CARBON DIOXIDE (TOXIC)'
        state_temperature = 280.0
        state_pressure = 8.0E+06
        vessel_shape = VesselShape.VESSEL_SPHERE
        vessel_diameter = 5.0
        leak_hole_diameter = 0.008
        time_varying_option = TimeVaryingOption.INITIAL_RATE
        leak_hole_height_fraction = 0.5
        surface_type = SurfaceType.WATER
        surface_roughness = 0.01
        wind_speed = 4.0
        stability_class = AtmosphericStabilityClass.STABILITY_C
        end_point_concentration = 0.0

    """

    # Set the case properties.
    material_name = 'CARBON DIOXIDE (TOXIC)'
    state_temperature = 280.0
    state_pressure = 8.0E+06
    vessel_shape = VesselShape.VESSEL_SPHERE
    vessel_diameter = 5.0
    leak_hole_diameter = 0.008
    time_varying_option = TimeVaryingOption.INITIAL_RATE
    leak_hole_height_fraction = 0.5
    surface_type = SurfaceType.WATER
    surface_roughness = 0.01
    wind_speed = 4.0
    stability_class = AtmosphericStabilityClass.STABILITY_C
    wind_profile_flag = WindProfileFlag.LOGARITHMIC_PROFILE
    end_point_concentration = 0.0

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
    vessel = Vessel(state = vessel_state_calculation.output_state, material = vessel_state_calculation.material, vessel_conditions = vessel_state_calculation.vessel_conditions, diameter = vessel_diameter, shape = vessel_shape, liquid_fill_fraction_by_volume = 0.8)

    # Create a leak to use in the vessel leak calculation.
    # The leak has a hole of diameter of 0.05m.  The time varying option is set topytest initial rate.
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

    # Set up the entities required by the dispersion calculation.
    substrate = Substrate(surface_type = surface_type, surface_roughness=surface_roughness)
    weather = Weather(wind_speed=wind_speed, stability_class=stability_class, wind_profile_flag=wind_profile_flag)
    dispersion_parameters = DispersionParameters()

    dispersion_calculation = DispersionCalculation(vessel_leak_calculation.exit_material, substrate, vessel_leak_calculation.discharge_result, vessel_leak_calculation.discharge_records, len(vessel_leak_calculation.discharge_records), weather, dispersion_parameters, end_point_concentration)

    print('Running dispersion_calculation...')
    resultCode = dispersion_calculation.run()

    # Print any messages.
    if len(dispersion_calculation.messages) > 0:
        print('Messages:')
        for message in dispersion_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        print(f'SUCCESS: dispersion_calculation ({dispersion_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED dispersion_calculation with result code {resultCode}'

    # Set up the entities required by the sideview calculation.
    dispersion_output_config = DispersionOutputConfig(concentration = end_point_concentration)

    # Set up the sideview calculation.
    sideview_at_time_calculation = SideviewAtTimeCalculation(scalar_udm_outputs= dispersion_calculation.scalar_udm_outputs, weather= weather, dispersion_records= dispersion_calculation.dispersion_records, dispersion_record_count= len(dispersion_calculation.dispersion_records), substrate=substrate, dispersion_output_config=dispersion_output_config, material=vessel_leak_calculation.exit_material, dispersion_parameters=dispersion_parameters)

    print('Running sideview_at_time_calculation...')
    resultCode = sideview_at_time_calculation.run()

    # Print any messages.
    if len(sideview_at_time_calculation.messages) > 0:
        print('Messages:')
        for message in sideview_at_time_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        if (len(sideview_at_time_calculation.contour_points) != 171):
            assert False, f'Reression failed with len(sideview_at_time_calculation.contour_points) = {len(sideview_at_time_calculation.contour_points)}'
        if (len(sideview_at_time_calculation.contour_points) > 0):
            if (abs((sideview_at_time_calculation.contour_points[len(sideview_at_time_calculation.contour_points)-3].x -   6.9777184369577)/  6.9777184369577) >1e-3):
                assert False, f'Regression failed with sideview_at_time_calculation.contour_points[len(sideview_at_time_calculation.contour_points)-3].x = {sideview_at_time_calculation.contour_points[len(sideview_at_time_calculation.contour_points)-3].x}'
        if (len(sideview_at_time_calculation.dispersion_records) > 0):
            if(abs((sideview_at_time_calculation.dispersion_records[len(sideview_at_time_calculation.dispersion_records)-1].centreline_concentration - 0.03998493262289725)/0.03998493262289725)>1e-3):
                assert False, f'Regression failed with sideview_at_time_calculation.dispersion_records[len(sideview_at_time_calculation.dispersion_records)-1].centreline_concentration = {sideview_at_time_calculation.dispersion_records[len(sideview_at_time_calculation.dispersion_records)-1].centreline_concentration}'
        print(f'SUCCESS: sideview_at_time_calculation ({sideview_at_time_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED sideview_at_time_calculation with result code {resultCode}'
