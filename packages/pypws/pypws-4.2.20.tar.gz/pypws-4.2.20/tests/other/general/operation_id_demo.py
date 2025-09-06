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


from pypws.calculations import GetMassFromVesselCalculation
from pypws.entities import Material, MaterialComponent, State, Vessel
from pypws.enums import ResultCode, VesselConditions, VesselShape


def operation_id_demo():
    
    """
    Test for get mass from vessel calculation with the following inputs

        material_name = 'CARBON DIOXIDE (TOXIC)'
        state_temperature = 280.0
        state_pressure = 8.0E+06
        vessel_shape = VesselShape.VESSEL_SPHERE
        vessel_diameter = 5.0
        
    """
    
    # Define the material.
    material = Material(
	    name="CARBON DIOXIDE (TOXIC)",
	    components=[
		    MaterialComponent(
			    name="CARBON DIOXIDE (TOXIC)",
			    mole_fraction=1.0
		    )
	    ]
    )
    
    # Define the properties.
    state_temperature = 280.0
    state_pressure = 8.0E+06
    vessel_shape = VesselShape.VESSEL_SPHERE
    vessel_diameter = 5.0
    
    # Create a vessel.
    vessel = Vessel(state = State(pressure= state_pressure, temperature = state_temperature, liquid_fraction = 0.8), material = material, diameter = vessel_diameter, shape = vessel_shape, vessel_conditions = VesselConditions.PRESSURIZED_LIQUID_VESSEL, liquid_fill_fraction_by_volume = 0.6)
    
    # Create a get mass from vessel calculation.
    get_mass_from_vessel_calculation = GetMassFromVesselCalculation(vessel = vessel)
    
    # Run the calculation.
    print ('Running get_mass_from_vessel_calculation')
    result_code = get_mass_from_vessel_calculation.run()

    print(f'operation_id: {get_mass_from_vessel_calculation.operation_id}')
    
    # Print any messages.
    if len(get_mass_from_vessel_calculation.messages) > 0:
        print('Messages:')
        for message in get_mass_from_vessel_calculation.messages:
            print(message)

    if result_code == ResultCode.SUCCESS:
        print(f'SUCCESS: get_mass_from_vessel_calculation ({get_mass_from_vessel_calculation.calculation_elapsed_time}ms)')
    else:
        assert False, f'FAILED get_mass_from_vessel_calculation with result code {result_code}'

operation_id_demo()