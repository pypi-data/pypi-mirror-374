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


from pypws.calculations import MixtureConstantPropertiesCalculation
from pypws.entities import Material, MaterialComponent, State
from pypws.enums import ResultCode


def test_case_97():

    # Set the material
    material = Material("NATURAL GAS", [MaterialComponent("METHANE", 0.85), MaterialComponent("ETHANE", 0.1), MaterialComponent("PROPANE", 0.05)], component_count = 3)

    # Create a mixture constant properties calculation using the material.
    mixture_constant_properties_calculation = MixtureConstantPropertiesCalculation(material)

    # Run the calculation
    print('Running mixture_constant_properties_calculation...')
    resultCode = mixture_constant_properties_calculation.run()

    # Print any messages.
    if len(mixture_constant_properties_calculation.messages) > 0:
        print('Messages:')
        for message in mixture_constant_properties_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        if (abs((mixture_constant_properties_calculation.mix_constant_prop_result.lower_flammability_limit - 0.04402515723270441) / 0.04402515723270441) > 1e-3):
            assert False, f'Regression failed with mixture_constant_properties_calculation lower_flammability_limit = {mixture_constant_properties_calculation.mix_constant_prop_result.lower_flammability_limit}'
        if (abs((mixture_constant_properties_calculation.mix_constant_prop_result.upper_flammability_limit - 0.14286869340232858) / 0.14286869340232858) > 1e-3):
            assert False, f'Regression failed with mixture_constant_properties_calculation upper_flammability_limit = {mixture_constant_properties_calculation.mix_constant_prop_result.upper_flammability_limit}'
        if (abs((mixture_constant_properties_calculation.mix_constant_prop_result.critical_pressure - 4608750.0) / 4608750.0) > 1e-3):
            assert False, f'Regression failed with mixture_constant_properties_calculation critical_pressure = {mixture_constant_properties_calculation.mix_constant_prop_result.critical_pressure}'
        if (abs((mixture_constant_properties_calculation.mix_constant_prop_result.critical_temperature - 210.991) / 210.991) > 1e-3):
            assert False, f'Regression failed with mixture_constant_properties_calculation critical_temperature = {mixture_constant_properties_calculation.mix_constant_prop_result.critical_temperature}'
        if (abs((mixture_constant_properties_calculation.mix_constant_prop_result.molecular_weight - 18.847806000000002) / 18.847806000000002) > 1e-3):
            assert False, f'Regression failed with mixture_constant_properties_calculation molecular_weight = {mixture_constant_properties_calculation.mix_constant_prop_result.molecular_weight}'
        if (abs((mixture_constant_properties_calculation.mix_constant_prop_result.bubble_point - 113.67514401917592) / 113.67514401917592) > 1e-3):
            assert False, f'Regression failed with mixture_constant_properties_calculation bubble_point = {mixture_constant_properties_calculation.mix_constant_prop_result.bubble_point}'
        print(f'SUCCESS: mixture_constant_properties_calculation ({mixture_constant_properties_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED mixture_constant_properties_calculation with result code {resultCode}'