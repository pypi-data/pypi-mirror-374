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
    MaxConcFootprintCalculation,
    VesselReliefValveCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    Bund,
    DischargeParameters,
    DispersionOutputConfig,
    DispersionParameters,
    Material,
    MaterialComponent,
    ReliefValve,
    State,
    Substrate,
    Vessel,
    VesselShape,
    Weather,
)
from pypws.enums import AtmosphericStabilityClass, ResultCode, SurfaceType, WindProfileFlag


def test_case_35():

    """
    Maximum concentration footprint calculation test case with the following properties:

        material_name = 'CHLORINE'
        state_temperature = 320.0
        state_pressure = 1.0E+06
        state_liquid_fraction=1.0
        vessel_shape = VesselShape.HORIZONTAL_CYLINDER
        vessel_diameter = 2.0
        vessel_length = 5.0
        relief_valve_pipe_diameter = 0.02
        relief_valve_pipe_length = 10.0
        relief_valve_pipe_height_fraction = 1
        relief_valve_constriction_diameter = 0.02
    """

    state_temperature = 320.0
    state_pressure = 1.0E+06
    state_liquid_fraction=1.0
    vessel_shape = VesselShape.HORIZONTAL_CYLINDER
    vessel_diameter = 2.0
    vessel_length = 5.0
    liquid_fill_fraction_by_volume = 0.7
    relief_valve_pipe_diameter = 0.02
    relief_valve_pipe_length = 10.0
    relief_valve_pipe_height_fraction = 1
    relief_valve_constriction_diameter = 0.02
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
    material = Material("CHLORINE", [MaterialComponent("CHLORINE", 1.0)])

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

    # Create a vessel to use in the relief valve calculation using the previously defined entities. The vessel is a horizontal cylinder with a diameter of 2m and a length of 5m.
    vessel = Vessel(state=state, material=material, vessel_conditions=vessel_state_calculation.vessel_conditions, liquid_fill_fraction_by_volume=liquid_fill_fraction_by_volume, shape=vessel_shape, diameter=vessel_diameter, length=vessel_length)

    # Create a relief valve to use in the vessel relief valve calculation. Pipe diameter is 0.02m, pipe length is 10m, and pipe height fraction is 1.
    relief_valve = ReliefValve(pipe_diameter=relief_valve_pipe_diameter, pipe_length= relief_valve_pipe_length, pipe_height_fraction= relief_valve_pipe_height_fraction, relief_valve_constriction_diameter=relief_valve_constriction_diameter)

    # Create a vessel relief valve calculation using the vessel, relief valve, and discharge parameters.
    vessel_relief_valve_calculation = VesselReliefValveCalculation(vessel, relief_valve, DischargeParameters())

    # Run a vessel relief valve calculation.
    print('Running vessel_relief_valve_calculation...')
    resultCode = vessel_relief_valve_calculation.run()

    # Print any messages.
    if len(vessel_relief_valve_calculation.messages) > 0:
        print('Messages:')
        for message in vessel_relief_valve_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        print(f'SUCCESS: vessel_relief_valve_calculation ({vessel_relief_valve_calculation.calculation_elapsed_time}ms)')
        print(f'vessel_relief_valve_calculation.discharge_result.release_mass: {vessel_relief_valve_calculation.discharge_result.release_mass} [kg]')
    else:
        assert False, f'FAILED vessel_relief_valve_calculation with result code {resultCode}'

    # Set up the entities required by the dispersion calculation.
    bund = Bund(specify_bund=specify_bund, bund_height=bund_height, bund_diameter=bund_diameter)
    substrate = Substrate(bund=bund, surface_type=surface_type, surface_roughness=surface_roughness)
    weather = Weather(wind_speed=wind_speed, stability_class=stability_class, wind_profile_flag=wind_profile_flag)
    dispersion_parameters = DispersionParameters()

    # Set up the dispersion calculation.
    dispersion_calculation = DispersionCalculation(vessel_relief_valve_calculation.exit_material, substrate, vessel_relief_valve_calculation.discharge_result, vessel_relief_valve_calculation.discharge_records, len(vessel_relief_valve_calculation.discharge_records), weather, dispersion_parameters, end_point_concentration)

    print('Running dispersion_calculation...')
    resultCode = dispersion_calculation.run()

    # Print any messages.
    if len(dispersion_calculation.messages) > 0:
        print('Messages:')
        for message in dispersion_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        print(f'SUCCESS: dispersion_calculation ({dispersion_calculation.calculation_elapsed_time}ms)')
        print(f'length dispersion records = {len(dispersion_calculation.dispersion_records)}')
        print(f'minimum concentration = {dispersion_calculation.scalar_udm_outputs.minimum_concentration}')
        print(f'observer count = {dispersion_calculation.scalar_udm_outputs.observer_count}')
        print(f'final centreline concentration = {dispersion_calculation.dispersion_records[len(dispersion_calculation.dispersion_records)-1].centreline_concentration}')
        print(f'final downwind distance = {dispersion_calculation.dispersion_records[len(dispersion_calculation.dispersion_records)-1].downwind_distance}')
        print(f'SUCCESS: dispersion_calculation ({dispersion_calculation.calculation_elapsed_time}ms)')        
        print(f'SUCCESS: dispersion_calculation ({dispersion_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED dispersion_calculation with result code {resultCode}'

    # Set up the entities required by the maximum concentration footprint calculation.
    dispersion_output_config = DispersionOutputConfig(concentration = end_point_concentration)

    # Set up the maximum concentration footprint calculation.
    max_conc_footprint_calculation = MaxConcFootprintCalculation(scalar_udm_outputs= dispersion_calculation.scalar_udm_outputs, weather= weather, dispersion_records= dispersion_calculation.dispersion_records, dispersion_record_count= len(dispersion_calculation.dispersion_records), substrate=substrate, dispersion_output_config=dispersion_output_config, material=vessel_relief_valve_calculation.exit_material, dispersion_parameters=dispersion_parameters)

    print('Running max_conc_footprint_calculation...')
    resultCode = max_conc_footprint_calculation.run()

    # Print any messages.
    if len(max_conc_footprint_calculation.messages) > 0:
        print('Messages:')
        for message in max_conc_footprint_calculation.messages:
            print(message)

    if resultCode == resultCode.SUCCESS:
        if (len(max_conc_footprint_calculation.contour_points)!=651):
            assert False,f'Regression failed with len(max_conc_footprint_calculation.contour_points) = {len(max_conc_footprint_calculation.contour_points)}'
        if (abs((max_conc_footprint_calculation.contour_points[len(max_conc_footprint_calculation.contour_points)-3].x-(3.5444266994358022))/(3.5444266994358022))>1e-3):
            assert False,f'Regression failed with max_conc_footprint_calculation.contour_points[len(max_conc_footprint_calculation.contour_points)-3].x = {max_conc_footprint_calculation.contour_points[len(max_conc_footprint_calculation.contour_points)-3].x}'
        print(f'SUCCESS: max_conc_footprint_calculation ({max_conc_footprint_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED max_conc_footprint_calculation with result code {resultCode}'