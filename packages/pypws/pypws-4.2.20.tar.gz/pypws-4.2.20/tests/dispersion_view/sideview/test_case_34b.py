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
    VesselLineRuptureCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    Bund,
    DischargeParameters,
    DispersionOutputConfig,
    DispersionParameters,
    LineRupture,
    Material,
    MaterialComponent,
    State,
    Substrate,
    Vessel,
    VesselShape,
    Weather,
)
from pypws.enums import AtmosphericStabilityClass, ResultCode, SurfaceType, WindProfileFlag


def test_case_34b():

    """
        Sideview at time calculation test case with the following properties:

        material_name = 'AMMONIA'
        state_temperature = 290.0
        state_pressure = float(7.0e6)
        state_liquid_fraction = 1.0
        vessel_shape = VesselShape.VESSEL_CUBOID
        vessel_height = 2.0
        vessel_width = 1.0
        vessel_length = 3.0
        pipe_diameter = 0.1
        pipe_length = 1.0
        pipe_height_fraction = 0.1
        surface_type = SurfaceType.LAND
        surface_roughness = 0.183
        wind_speed = 1.5
        stability_class = AtmosphericStabilityClass.STABILITY_D
        end_point_concentration = 0.0
        specify_bund = True
        bund_height = .5
        bund_diameter = 5.0
    """

    state_temperature = 290.0
    state_pressure = float(7.0e6)
    state_liquid_fraction = 1.0
    surface_type = SurfaceType.LAND
    surface_roughness = 0.183
    wind_speed = 1.5
    stability_class = AtmosphericStabilityClass.STABILITY_D
    wind_profile_flag = WindProfileFlag.LOGARITHMIC_PROFILE
    end_point_concentration = 0.0
    specify_bund = True
    bund_height = .5
    bund_diameter = 5.0

    # Define the initial state of the vessel.
    state = State(temperature=state_temperature, pressure=state_pressure, liquid_fraction=state_liquid_fraction)

    # Define the material contained by the vessel.
    material = Material("AMMONIA", [MaterialComponent("AMMONIA", 1.0)])

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

    # Create a vessel to use in the line rupture calculation using the previously defined entities. The vessel is a cuboid with a height of 2m, width of 1m, and length of 3m.
    vessel = Vessel(state=state, material=material, vessel_conditions=vessel_state_calculation.vessel_conditions, liquid_fill_fraction_by_volume=0.7, shape=VesselShape.VESSEL_CUBOID, height=2, width=1, length = 3)

    # Create a line rupture to use in the vessel line rupture calculation.Pipe diameter is 0.1m, pipe length is 1m, and pipe height fraction is 0.1.
    line_rupture = LineRupture(pipe_diameter=0.1, pipe_length=1.0, pipe_height_fraction=0.1)

    # Create a vessel line rupture calculation using the vessel, line rupture, and discharge parameters.
    vessel_line_rupture_calculation = VesselLineRuptureCalculation(vessel, line_rupture, DischargeParameters())

    # Run a vessel line rupture calculation.
    print('Running vessel_line_rupture_calculation...')
    resultCode = vessel_line_rupture_calculation.run()

    # Print any messages.
    if len(vessel_line_rupture_calculation.messages) > 0:
        print('Messages:')
        for message in vessel_line_rupture_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        print(f'SUCCESS: vessel_line_rupture_calculation ({vessel_line_rupture_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED vessel_line_rupture_calculation with result code {resultCode}'

    # Set up the entities required by the dispersion calculation.
    bund = Bund(specify_bund=specify_bund, bund_height=bund_height, bund_diameter=bund_diameter)
    substrate = Substrate(bund=bund, surface_type=surface_type, surface_roughness=surface_roughness)
    weather = Weather(wind_speed=wind_speed, stability_class=stability_class, wind_profile_flag = WindProfileFlag.LOGARITHMIC_PROFILE)
    dispersion_parameters = DispersionParameters()

    # Set up the dispersion calculation.
    dispersion_calculation = DispersionCalculation(vessel_line_rupture_calculation.exit_material, substrate, vessel_line_rupture_calculation.discharge_result, vessel_line_rupture_calculation.discharge_records, len(vessel_line_rupture_calculation.discharge_records), weather, dispersion_parameters, end_point_concentration)

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
    sideview_at_time_calculation = SideviewAtTimeCalculation(scalar_udm_outputs= dispersion_calculation.scalar_udm_outputs, weather= weather, dispersion_records= dispersion_calculation.dispersion_records, dispersion_record_count= len(dispersion_calculation.dispersion_records), substrate=substrate, dispersion_output_config=dispersion_output_config, material=vessel_line_rupture_calculation.exit_material, dispersion_parameters=dispersion_parameters)

    print('Running sideview_at_time_calculation...')
    resultCode = sideview_at_time_calculation.run()

    # Print any messages.
    if len(sideview_at_time_calculation.messages) > 0:
        print('Messages:')
        for message in sideview_at_time_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        if (len(sideview_at_time_calculation.contour_points) != 56):
            assert False, f'Reression failed with len(sideview_at_time_calculation.contour_points) = {len(sideview_at_time_calculation.contour_points)}'
        if (len(sideview_at_time_calculation.contour_points) > 0):
            if (abs((sideview_at_time_calculation.contour_points[len(sideview_at_time_calculation.contour_points)-3].x -  288.38690766280035)/ 288.38690766280035) >1e-3):
                assert False, f'Regression failed with sideview_at_time_calculation.contour_points[len(sideview_at_time_calculation.contour_points)-3].x = {sideview_at_time_calculation.contour_points[len(sideview_at_time_calculation.contour_points)-3].x}'
        if (len(sideview_at_time_calculation.dispersion_records) > 0):
            if(abs((sideview_at_time_calculation.dispersion_records[len(sideview_at_time_calculation.dispersion_records)-1].centreline_concentration - 0.0005178235809216942)/0.0005178235809216942)>1e-3):
                assert False, f'Regression failed with sideview_at_time_calculation.dispersion_records[len(sideview_at_time_calculation.dispersion_records)-1].centreline_concentration = {sideview_at_time_calculation.dispersion_records[len(sideview_at_time_calculation.dispersion_records)-1].centreline_concentration}'
        print(f'SUCCESS: sideview_at_time_calculation ({sideview_at_time_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED sideview_at_time_calculation with result code {resultCode}'
