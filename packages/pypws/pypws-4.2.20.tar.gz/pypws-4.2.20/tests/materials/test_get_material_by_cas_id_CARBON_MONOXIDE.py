import os
import pathlib
import sys
from pickle import GET

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


from pypws.materials import get_material_by_cas_id
from pypws.utilities import where

def test_get_material_by_casid_CARBON_MONOXIDE():

    """
    Test to get the material by CASID for CARBON MONOXIDE.
        
    """

    # Invoke the method.
    print ('Running get_material_by_cas_id')
    materials = get_material_by_cas_id('630080')

    # Assert that the material is not None and that CARBON MONOXIDE has been returned..
    assert materials is not None, 'No materials returned'
    assert len(materials) > 0, 'A material matching the CAS ID was not returned'
    assert where(materials, lambda x: x.name == 'CARBON MONOXIDE') is not None, 'CARBON MONOXIDE not returned'

    for material in materials:
        print ('Material:', material)

