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


def test_case_137():
    # Define the test case properties.
    material_name = 'BUTANE_DECANE_ETHANE'
    composition_moles = [0.4, 0.2, 0.4]

    # Define the material
    material = Material(name = material_name, components = [MaterialComponent(name = 'N-BUTANE', mole_fraction=0.4), 
                                                            MaterialComponent(name = 'N-DECANE', mole_fraction= 0.2),
                                                            MaterialComponent(name = 'ETHANE', mole_fraction= 0.4)], component_count= 3)

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
        if (abs(convert_comp_mole_to_mass_calculation.composition_mass[0]-0.364786643038023)/0.364786643038023 > 1e-3):
            assert False, f'Regression failed with convert_comp_mole_to_mass_calculation.composition_mole[0] = {convert_comp_mole_to_mass_calculation.composition_mass[0]}'
        print(f'SUCCESS: convert_comp_mole_to_mass_calculation ({convert_comp_mole_to_mass_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED convert_comp_mole_to_mass_calculation with result code {resultCode}'