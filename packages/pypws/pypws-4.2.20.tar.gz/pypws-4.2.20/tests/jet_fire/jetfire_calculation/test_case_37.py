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
    VesselLeakCalculation,
    VesselStateCalculation,
)
from pypws.entities import (
    DischargeParameters,
    FlammableParameters,
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
    TimeVaryingOption,
    VesselShape,
)


def test_case_37():
    
    """
    Jet fire calculation test case with the following properties:

        material_name = 'N-BUTANE'
        state_temperature = 300.0
        state_pressure = 3.0E+05
        vessel_shape = VesselShape.VESSEL_CUBOID
        vessel_height = 2.0
        vessel_width = 1.0
        vessel_length = 3.0
        leak_hole_diameter = 0.05
        time_varying_option = TimeVaryingOption.INITIAL_RATE
        leak_hole_height_fraction = 0.2
        wind_speed = 2.0
        stability_class = STABILITY_F
        surface_roughness = 0.18
        time_of_interest = 10.0
    """

    # Set the case properties.
    material_name = 'N-BUTANE'
    state_temperature = 300.0
    state_pressure = 3.0E+05
    vessel_shape = VesselShape.VESSEL_CUBOID
    vessel_height = 2.0
    vessel_width = 1.0
    vessel_length = 3.0
    leak_hole_diameter = 0.05
    liquid_fill_fraction_by_volume = 0.5
    time_varying_option = TimeVaryingOption.INITIAL_RATE
    leak_hole_height_fraction = 0.2
    wind_speed = 2.0
    stability_class = AtmosphericStabilityClass.STABILITY_F
    surface_roughness = 0.18
    time_of_interest = 20.0
    jet_fire_auto_select = False
    time_averaging = True

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
    # All other values are defaulted.
    vessel = Vessel(state = vessel_state_calculation.output_state, 
                    material = vessel_state_calculation.material, 
                    vessel_conditions = vessel_state_calculation.vessel_conditions,
                    length = vessel_length,
                    width = vessel_width,
                    height = vessel_height, 
                    shape = vessel_shape, 
                    liquid_fill_fraction_by_volume = liquid_fill_fraction_by_volume)

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

    # Instantiate the data required by the jet fire calculation.
    weather = Weather(wind_speed = wind_speed, stability_class = stability_class)
    substrate = Substrate(surface_roughness = surface_roughness)
    flammable_parameters = FlammableParameters(time_of_interest = time_of_interest, jet_fire_auto_select = jet_fire_auto_select, time_averaging = time_averaging)

    # Create a jet fire calculation using the required input data.
    jet_fire_calculation = JetFireCalculation(vessel_leak_calculation.exit_material, vessel_leak_calculation.discharge_records, len(vessel_leak_calculation.discharge_records), vessel_leak_calculation.discharge_result, weather, substrate, flammable_parameters)

    # Run the jet fire calculation.
    print('Running jet_fire_calculation...')
    resultCode = jet_fire_calculation.run()

    # Print any messages.
    if len(jet_fire_calculation.messages) > 0:
        print('Messages:')
        for message in jet_fire_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (abs((jet_fire_calculation.flame_result.flame_length- 52.735663839470966)/ 52.735663839470966)>1e-3):
            assert False,f'Regression failed with jet_fire_calculation.flame_result.flame_length = {jet_fire_calculation.flame_result.flame_length}'
        if (abs((jet_fire_calculation.flame_result.surface_emissive_power-199020.3679914611)/199020.3679914611)>1e-3):
            assert False,f'Regression failed with jet_fire_calculation.flame_result.surface_emissive_power = {jet_fire_calculation.flame_result.surface_emissive_power}'
        if (len(jet_fire_calculation.flame_records) != 2):
            assert False,f'Regression failed with len(jet_fire_calculation.flame_records = {len(jet_fire_calculation.flame_records)}'
        print(f'SUCCESS: jet_fire_calculation ({jet_fire_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED jet_fire_calculation with result code {resultCode}'