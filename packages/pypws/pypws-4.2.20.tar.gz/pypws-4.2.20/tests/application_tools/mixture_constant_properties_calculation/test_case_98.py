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


def test_case_98():

    # Set the material
    material = Material("GASOLINE", [MaterialComponent("N-OCTANE", 0.77), MaterialComponent("N-HEPTANE", 0.13), MaterialComponent("N-NONANE", 0.05), MaterialComponent("TOLUENE", 0.05)], component_count = 4)

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
        if (abs((mixture_constant_properties_calculation.mix_constant_prop_result.lower_flammability_limit - 0.00970712693329131) / 0.00970712693329131) > 1e-3):
            assert False, f'Regression failed with mixture_constant_properties_calculation lower_flammability_limit = {mixture_constant_properties_calculation.mix_constant_prop_result.lower_flammability_limit}'
        if (abs((mixture_constant_properties_calculation.mix_constant_prop_result.upper_flammability_limit - 0.06500456558538582) / 0.06500456558538582) > 1e-3):
            assert False, f'Regression failed with mixture_constant_properties_calculation upper_flammability_limit = {mixture_constant_properties_calculation.mix_constant_prop_result.upper_flammability_limit}'
        if (abs((mixture_constant_properties_calculation.mix_constant_prop_result.critical_pressure - 2593400.0) / 2593400.0) > 1e-3):
            assert False, f'Regression failed with mixture_constant_properties_calculation critical_pressure = {mixture_constant_properties_calculation.mix_constant_prop_result.critical_pressure}'
        if (abs((mixture_constant_properties_calculation.mix_constant_prop_result.critical_temperature - 567.4425) / 567.4425) > 1e-3):
            assert False, f'Regression failed with mixture_constant_properties_calculation critical_temperature = {mixture_constant_properties_calculation.mix_constant_prop_result.critical_temperature}'
        if (abs((mixture_constant_properties_calculation.mix_constant_prop_result.molecular_weight - 112.00188860000002) / 112.00188860000002) > 1e-3):
            assert False, f'Regression failed with mixture_constant_properties_calculation molecular_weight = {mixture_constant_properties_calculation.mix_constant_prop_result.molecular_weight}'
        if (abs((mixture_constant_properties_calculation.mix_constant_prop_result.bubble_point - 393.99970870791725) / 393.99970870791725) > 1e-3):
            assert False, f'Regression failed with mixture_constant_properties_calculation bubble_point = {mixture_constant_properties_calculation.mix_constant_prop_result.bubble_point}'
        print(f'SUCCESS: mixture_constant_properties_calculation ({mixture_constant_properties_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED mixture_constant_properties_calculation with result code {resultCode}'