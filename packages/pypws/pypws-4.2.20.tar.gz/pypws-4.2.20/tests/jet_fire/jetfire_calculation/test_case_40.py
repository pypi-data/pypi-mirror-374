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
    VesselLineRuptureCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    DischargeParameters,
    FlammableParameters,
    LineRupture,
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
    VesselShape,
)


def test_case_40():
    
    """
    Jet fire calculation test case with the following properties:

    material_name = "ETHANE_METHANE_HYDROGEN"
    state_temperature = 260.0
    state_pressure = 5.0E+05
    vessel_shape = VesselShape.VESSEL_SPHERE
    vessel_diameter = 3.0
    liquid_fill_fraction_by_volume = 0.7
    pipe_diameter = 0.5
    pipe_length = 1.0
    pipe_height_fraction = 0.5
    wind_speed = 2.0
    stability_class = AtmosphericStabilityClass.STABILITY_F
    surface_roughness = 0.18
    time_of_interest = 600.0
    jet_fire_auto_select = False
    time_averaging = True

    """

    # Set the case properties.
    material_name = "ETHANE_METHANE_HYDROGEN"
    state_temperature = 260.0
    state_pressure = 5.0E+05
    vessel_shape = VesselShape.VESSEL_SPHERE
    vessel_diameter = 3.0
    liquid_fill_fraction_by_volume = 0.7
    pipe_diameter = 0.5
    pipe_length = 1.0
    pipe_height_fraction = 0.5
    wind_speed = 2.0
    stability_class = AtmosphericStabilityClass.STABILITY_F
    surface_roughness = 0.18
    time_of_interest = 600.0
    jet_fire_auto_select = False
    time_averaging = True

    # Define the initial state of the vessel.
    state = State(temperature = state_temperature, pressure = state_pressure, liquid_fraction = 0.0)

    # Define the material contained by the vessel.
    material = Material(material_name, [MaterialComponent("METHANE", 0.5), MaterialComponent("ETHANE", 0.3), MaterialComponent("HYDROGEN", 0.2)], component_count = 3)

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
    vessel = Vessel(state = vessel_state_calculation.output_state, 
                    material = vessel_state_calculation.material, 
                    vessel_conditions = vessel_state_calculation.vessel_conditions,
                    diameter= vessel_diameter,
                    length = 5.0,
                    shape = vessel_shape, 
                    liquid_fill_fraction_by_volume = liquid_fill_fraction_by_volume)

    # Create a line rupture to use in the vessel line rupture calculation.
    line_rupture = LineRupture(pipe_diameter = pipe_diameter, pipe_length = pipe_length, pipe_height_fraction = pipe_height_fraction)

    # Create a vessel line rupture calculation using the vessel, line rupture, and discharge parameters.
    vessel_line_rupture_calculation = VesselLineRuptureCalculation(vessel, line_rupture, DischargeParameters())

    # Run the vessel line rupture calculation.
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

    # Instantiate the data required by the jet fire calculation.
    weather = Weather(wind_speed = wind_speed, stability_class = stability_class)
    substrate = Substrate(surface_roughness = surface_roughness)
    flammable_parameters = FlammableParameters(time_of_interest = time_of_interest, jet_fire_auto_select = jet_fire_auto_select, time_averaging = time_averaging)

    # Create a jet fire calculation using the required input data.
    jet_fire_calculation = JetFireCalculation(vessel_line_rupture_calculation.exit_material, vessel_line_rupture_calculation.discharge_records, len(vessel_line_rupture_calculation.discharge_records), vessel_line_rupture_calculation.discharge_result, weather, substrate, flammable_parameters)

    # Run the jet fire calculation.
    print('Running jet_fire_calculation...')
    resultCode = jet_fire_calculation.run()

    # Print any messages.
    if len(jet_fire_calculation.messages) > 0:
        print('Messages:')
        for message in jet_fire_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (abs((jet_fire_calculation.flame_result.flame_length- 96.77758243403922)/ 96.77758243403922)>1e-3):
            assert False,f'Regression failed with jet_fire_calculation.flame_result.flame_length = {jet_fire_calculation.flame_result.flame_length}'
        if (abs((jet_fire_calculation.flame_result.surface_emissive_power-350000.0)/350000.0)>1e-3):
            assert False,f'Regression failed with jet_fire_calculation.flame_result.surface_emissive_power = {jet_fire_calculation.flame_result.surface_emissive_power}'
        if (len(jet_fire_calculation.flame_records) != 2):
            assert False,f'Regression failed with len(jet_fire_calculation.flame_records = {len(jet_fire_calculation.flame_records)}'
        print(f'SUCCESS: jet_fire_calculation ({jet_fire_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED jet_fire_calculation with result code {resultCode}'