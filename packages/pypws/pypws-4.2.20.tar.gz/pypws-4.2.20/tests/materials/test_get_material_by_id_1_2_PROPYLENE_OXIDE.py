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


from pypws.materials import get_material_by_id

def test_get_material_by_id_1_2_PROPYLENE_OXIDE():

    """
    Test to get the material component data by id for 1,2-PROPYLENE OXIDE.
    1,2-PROPYLENE OXIDE component entity id = 8e8525ec-40cb-4afe-98a6-951f602b2c45.
        
    """

    # Invoke the method.
    print ('Running get_material_by_id')
    material = get_material_by_id('00b93527-dcea-48b6-bc03-a98aae6e630a')

    # Assert that the material component data is not None and that METHANE has been returned..
    assert material is not None, 'Material not returned'
    assert material.name == '1,2-PROPYLENE OXIDE', '1,2-PROPYLENE OXIDE not returned'

    print ('Material:', material)

