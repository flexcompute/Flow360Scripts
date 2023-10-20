# Get started with BET translators

This directory contains example scripts showing how to run:
- DFDC -> Flow360 Bet disk translator
- Xrotor -> Flow360 Bet disk translator
- C81 -> Flow360 Bet disk translator
- xfoil -> Flow360 Bet disk translator

## Dependencies

```
pip install -U flow360-betdisk
```

## Run

To run:
```
python3 DFDCtoFlow360BET.py
```
```
python3 XrotorToFlow360BET.py 
```
```
python3 XfoilToFlow360BET.py
```
```
python3 C81toFlow360BET.py
```


All the data used in these examples is in `./data` directory.

In the examples, we also provided the `flow360_XV15_BET_Template.json` file. It is a sample Flow360 input JSON file to which we will add the BET disk information. The final product of the examples scripts above will be a ready to run complete flow360 input json file. 


# Developers

to run these examples against source code
add these lines at the beginning of the example scripts:
```python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/BETDisk')))
```
