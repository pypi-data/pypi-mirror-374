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


from pypws.materials import get_material_by_name

def test_get_material_by_name_METHANE():

    """
    Test to get the material component data by name for METHANE.
        
    """

    # Invoke the method.
    print ('Running get_material_by_name')
    material = get_material_by_name('METHANE')

    # Assert that the material component data is not None and that METHANE has been returned.
    assert material is not None, 'Material not returned'
    assert material.name == 'METHANE', 'METHANE not returned'

    print ('Material:', material)

