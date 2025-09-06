import os
import pathlib
import sys

# When running locally the environment variable PYPWS_RUN_LOCALLY needs to be set to True.
# Check if the environment variable is set
if os.getenv('PYPWS_RUN_LOCALLY') != None and os.getenv('PYPWS_RUN_LOCALLY').lower() == 'true':
    # Navigate to the PYPWS directory by searching upwards until it is found.
    current_dir = pathlib.Path(__file__).resolve()

    while current_dir.name.lower() != 'package':
        current_dir = current_dir.parent

    # Insert the path to the pypws package into sys.path.
    sys.path.insert(0, f'{current_dir}')

from pypws.calculations import (
    VesselLeakMaxFlammableCloudCalculation,
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
    Resolution,
    ResultCode,
    SpecialConcentration,
    SurfaceType,
    TimeVaryingOption,
    VesselShape,
    WindProfileFlag
)

"""
This sample demonstrates how to use the vessel leak maximum flammable cloud calculation along with with the dependent entities.
"""

def test_case_94():

    # Set the case properties.
    material_name = 'N-PENTANE'
    state_temperature = 280.0
    state_pressure = 1.50E+05
    vessel_shape = VesselShape.HORIZONTAL_CYLINDER
    vessel_length = 5.0
    vessel_diameter = 2.0
    leak_hole_diameter = 0.05
    time_varying_option = TimeVaryingOption.TIME_VARYING_RATE
    leak_hole_height_fraction = 0.0

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
    vessel = Vessel(state = vessel_state_calculation.output_state, material = vessel_state_calculation.material, vessel_conditions = vessel_state_calculation.vessel_conditions, diameter = vessel_diameter, length = vessel_length, shape = vessel_shape, liquid_fill_fraction_by_volume = 0.5)

    # Create a leak to use in the vessel leak calculation.
    # The leak has a hole of diameter of 0.05m.  The time varying option is set topytest initial rate.
    leak = Leak(hole_diameter = leak_hole_diameter, hole_height_fraction = leak_hole_height_fraction , time_varying_option = time_varying_option)

    # Create discharge parameters to use in the vessel leak calculation taking all the default values.
    discharge_parameters = DischargeParameters()

    # Define the weather
    weather = Weather(wind_speed = 5.0, stability_class = AtmosphericStabilityClass.STABILITY_D, wind_profile_flag = WindProfileFlag.LOGARITHMIC_PROFILE)

    # Define the substrate
    substrate = Substrate(surface_roughness = 0.2, surface_type = SurfaceType.LAND)

    # Define the dispersion parameters
    dispersion_parameters = DispersionParameters()

    # Define the dispersion output configuration
    dispersion_output_config = DispersionOutputConfig(special_concentration = SpecialConcentration.LFL_FRACTION, resolution = Resolution.HIGH, elevation=0.0)

    # Create the vessel leak maximum flammable cloud calculation using the previously defined entities.
    vessel_leak_max_flammable_cloud_calculation = VesselLeakMaxFlammableCloudCalculation(vessel=vessel, leak=leak, discharge_parameters=discharge_parameters, weather=weather, substrate=substrate, dispersion_parameters=dispersion_parameters, dispersion_output_config=dispersion_output_config)

    # Run the calculation.
    print('Running vessel_leak_max_flammable_cloud_calculation...')
    resultCode = vessel_leak_max_flammable_cloud_calculation.run()

    # Print any messages.
    if len(vessel_leak_max_flammable_cloud_calculation.messages) > 0:
        print('Messages:')
        for message in vessel_leak_max_flammable_cloud_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (vessel_leak_max_flammable_cloud_calculation.vessel_leak_max_flammable_cloud_results.phase != 3):
            assert False,f'Regression failed with vessel_leak_max_flammable_cloud_calculation.vessel_leak_max_flammable_cloud_results.phase = {vessel_leak_max_flammable_cloud_calculation.vessel_leak_max_flammable_cloud_results.phase}'
        if (abs((vessel_leak_max_flammable_cloud_calculation.vessel_leak_max_flammable_cloud_results.lfl_extent- 15.196817260385107)/ 15.196817260385107)>1e-3):
            assert False,f'Regression failed with vessel_leak_max_flammable_cloud_calculation.vessel_leak_max_flammable_cloud_results.lfl_extent = {vessel_leak_max_flammable_cloud_calculation.vessel_leak_max_flammable_cloud_results.lfl_extent}'
        if (abs((vessel_leak_max_flammable_cloud_calculation.vessel_leak_max_flammable_cloud_results.lfl_area- 407.2282363319728)/ 407.2282363319728)>1e-3):
            assert False,f'Regression failed with vessel_leak_max_flammable_cloud_calculation.vessel_leak_max_flammable_cloud_results.lfl_area = {vessel_leak_max_flammable_cloud_calculation.vessel_leak_max_flammable_cloud_results.lfl_area}'
        if (abs((vessel_leak_max_flammable_cloud_calculation.vessel_leak_max_flammable_cloud_results.lfl_height-  0.3118404430192289)/ 0.3118404430192289)>1e-3):
            assert False,f'Regression failed with vessel_leak_max_flammable_cloud_calculation.vessel_leak_max_flammable_cloud_results.lfl_height = {vessel_leak_max_flammable_cloud_calculation.vessel_leak_max_flammable_cloud_results.lfl_height}'
        print(f'SUCCESS: vessel_leak_max_flammable_cloud_calculation ({vessel_leak_max_flammable_cloud_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED vessel_leak_max_flammable_cloud_calculation with result code {resultCode}'