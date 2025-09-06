import os
import pathlib
import sys

run_locally = os.getenv('PYPWS_RUN_LOCALLY')
if run_locally and run_locally.lower() == 'true':
    # Navigate to the PYPWS directory by searching upwards until it is found.
    current_dir = pathlib.Path(__file__).resolve()

    while current_dir.name.lower() != 'package':
        if current_dir.parent == current_dir:  # Check if the current directory is the root directory
            raise FileNotFoundError("The 'pypws' directory was not found in the path hierarchy.")
        current_dir = current_dir.parent

    # Insert the path to the pypws package into sys.path.
    sys.path.insert(0, f'{current_dir}')

from pypws.calculations import ConvertCompositionMoleToMassCalculation
from pypws.entities import Material, MaterialComponent
from pypws.enums import ResultCode


def test_case_136():
    # Define the test case properties.
    material_name = 'ETHANE_METHANE_HYDROGEN'
    composition_moles = [0.1, 0.3, 0.6]

    # Define the material
    material = Material(name = material_name, components = [MaterialComponent(name = 'ETHANE', mole_fraction=0.1), 
                                                            MaterialComponent(name = 'METHANE', mole_fraction= 0.3),
                                                            MaterialComponent(name = 'HYDROGEN', mole_fraction= 0.6)], component_count= 3)

    # Create a convert composition mole to mass calculation using the material and composition moles.
    convert_comp_mole_to_mass_calculation = ConvertCompositionMoleToMassCalculation(mixture=material,
                                                                                    composition_moles=composition_moles,
                                                                                    composition_moles_count=len(composition_moles))

    # Run the convert composition mole to mass calculation.
    print('Running convert_comp_mole_to_mass_calculation...')
    resultCode = convert_comp_mole_to_mass_calculation.run()

    # Print any messages.
    if len(convert_comp_mole_to_mass_calculation.messages) > 0:
        print('Messages:')
        for message in convert_comp_mole_to_mass_calculation.messages:
            print(message)

    if resultCode == ResultCode.SUCCESS:
        print (f'Mole fraction: {convert_comp_mole_to_mass_calculation.composition_moles}')
        print (f'Mass fraction: {convert_comp_mole_to_mass_calculation.composition_mass}')
        if (abs(convert_comp_mole_to_mass_calculation.composition_mass[0]-0.3330203480316813)/0.3330203480316813 > 1e-3):
            assert False, f'Regression failed with convert_comp_mole_to_mass_calculation.composition_mole[0] = {convert_comp_mole_to_mass_calculation.composition_mass[0]}'
        print(f'SUCCESS: convert_comp_mole_to_mass_calculation ({convert_comp_mole_to_mass_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED convert_comp_mole_to_mass_calculation with result code {resultCode}'