# PHAST WEB SERVICES

## Introduction

Phast is the world's most comprehensive process hazard analysis software which models the progress of a potential incident from the initial release to far-field dispersion including modelling of pool spreading and evaporation and resulting flammable and toxic effects. In Phast Web Services we have taken the same state of the art consequence modelling calculations and made them available as web services so you can use them in your own applications.

## Consequence analysis

Phast Web services and Python PWS have been developed to enable you to call Phast consequence calculations from within your own Python scripts.

We have services available for a wide range of consequence calculations:

- Discharge
- Toxic/flammable gas dispersion
- Fire and explosion modelling
- Various supporting, utility calculations

## Reference documentation
A detailed reference document for Phast Web Services can be found [here](https://phastwebservices.dnv.com/).

## Getting started
In order to create a Python script that is able to call the Phast Web Services calculations you will need to obtain an access token from DNV.  

Please note that the PyPWS library is tested on Python versions 3.11 onwards. It is recommended to use one of these versions.

## Sample code to perform a vessel leak calculation
In the following example the **VesselLeakCalculation** is used to predict the release of Methane from a 50mm hole in a horizontal vessel.  In order to get the correct conditions within the vessel the **VesselStateCalculation** is called first and the results from this are passed to the **VesselLeakCalculation** to correctly set it up.

```python
from pypws.calculations import VesselLeakCalculation, VesselStateCalculation
from pypws.entities import DischargeParameters, Leak, Material, MaterialComponent, State, Vessel
from pypws.enums import ResultCode, TimeVaryingOption, VesselShape

# Define the material contained by the vessel.
material = Material(material_name, [MaterialComponent(material_name, 1.0)])

# Define the initial state of the vessel.
state = State(temperature=state_temperature, pressure=state_pressure, liquid_fraction=0.0)

# Create a vessel state calculation using the material and state.
vessel_state_calculation = VesselStateCalculation(material, state)

# Run the vessel state calculation.
vessel_state_calculation.run()

# Create a vessel entity and pass in the results from the VesselStateCalculation.
vessel = Vessel(state=vessel_state_calculation.output_state, material=vessel_state_calculation.material, vessel_conditions=vessel_state_calculation.vessel_conditions, diameter=6.0, length=10.0, shape=VesselShape.HORIZONTAL_CYLINDER, liquid_fill_fraction_by_volume=0.0)

# Create a leak to use in the vessel leak calculation.
# The leak has a hole of diameter of 50mm but we specify it as 0.05 as all calculations are performed using
# SI units which in this case is metres.  The hole height fraction is set to 0.0 which corresponds to the
# bottom of the vessel.  The time varying option is set topytest initial rate.
leak = Leak(hole_diameter=0.05, hole_height_fraction=0.0, time_varying_option=TimeVaryingOption.INITIAL_RATE)

# Create discharge parameters to use in the vessel leak calculation taking all the default values.
discharge_parameters = DischargeParameters()

# Create a vessel leak calculation using the vessel, leak, and discharge parameters.
vessel_leak_calculation = VesselLeakCalculation(vessel, leak, discharge_parameters)

# Run the vessel leak calculation.
result_code = vessel_leak_calculation.run()

if resultCode == ResultCode.SUCCESS:
    print('SUCCESS: vessel_leak_calculation')
else:
    print(f'FAILED vessel_leak_calculation with result code {resultCode}')
    assert False

# Print any messages.
if len(vessel_leak_calculation.messages) > 0:
    print('Messages:')
    for message in vessel_leak_calculation.messages:
        print(message)
```

Note that each calculation returns a "Result Code" which can be used to check whether the calculation was successful.  In the event of a failed calculation another property (messages) of the calculation instance can be inspected to display possible reasons for the failed calculation.  These two features are only shown for the vessel_leak_calculation for reasons of brevity.