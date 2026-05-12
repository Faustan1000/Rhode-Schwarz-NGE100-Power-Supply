# Python Package for R&S NGE102B / 103B series Power supply
Tested on NGE102B but probably also works on NGE103B 
![](https://assets.rohde-schwarz.com/public/image/products/test-and-measurement/powersupplies/dc-powersupplies/dc-powersupplies-hardware/nge100b//rs-nge100b-powersupply-series-front-low-rohde-schwarz_200_66630_1024_576_1.jpg)
## How 2 use

after installing the package and activating an environment:

### Use as a python lib
install the package in your environment
```bash
pip install https://github.com/Faustan1000/Rhode-Schwarz-NGE100-Power-Supply/releases/download/v0.1.2/rs_power_supply-0.1.2-py3-none-any.whl
```
example:
```bash
from rs_power_supply import NGE100

# VISA resource string of the power supply
RESOURCE = "USB0::0x0AAD::0x0135::123456::INSTR"

# Use context manager for automatic cleanup
with NGE100(RESOURCE) as psu:

    # Select channel 1
    psu.select_channel(1)

    # Configure voltage, current and enable output
    psu.configure(
        voltage=12.0,   # Set output voltage to 12V
        current=1.5,    # Set current limit to 1.5A
        output=True     # Enable output
    )

    # Enable fuse protection
    psu.set_fuse(
        state=True
    )

    # Measure voltage
    voltage = psu.measure_voltage()
    print("Voltage:", voltage, "V")

    # Measure current
    current = psu.measure_current()
    print("Current:", current, "A")

    # Measure all available values
    values = psu.measure_all()

    print("Measured values:")
    print("Voltage:", values["voltage"], "V")
    print("Current:", values["current"], "A")
    print("Fuse:", values["fuse"])

    # Read fuse status separately
    fuse_status = psu.get_fuse_status()
    print("Fuse status:", fuse_status)

    # Check if fuse was triggered
    tripped = psu.fuse_tripped()
    print("Fuse tripped:", tripped)

    # Reset fuse if necessary
    psu.reset_fuse()

    # Disable output again
    psu.configure(
        output=False
    )

    # Disable fuse protection
    psu.set_fuse(
        state=False
    )
```
### Use as a Cli tool
- create a venv
```bash
python -m venv .venv
```
- install package 
```bash
pip install https://github.com/Faustan1000/Rhode-Schwarz-NGE100-Power-Supply/releases/download/v0.1.2/rs_power_supply-0.1.2-py3-none-any.whl
```
find resources:
```bash
NGE100 --list
```

Control the Power Supply (example)
```bash
NGE100 --channel 1 --volt 5 --curr 1 --off --fuse --measure all --resource USB0::----::INSTR
```
available arguments:
- list : lists all available Devices
- channel : selects a channel 
- volt : selects voltage 
- curr : selects maximum current
- on/off : switches on/off the channel
- fuse : switches on the fuse option on the NGE10xB
- resource : selects a resource connected to the pc (USB only!!!)
- config : selects a config file which can define all parameters listed here

### (Option) config file

instead of typing in all arguments by itself there is also the option to create a config file which contains all information

currently it is only possible to configure 1 channel per config file.

example file (config.txt)
```bash
--channel 1
--volt 5
--curr 1
--off
--resource USB0::----::INSTR
```

Use the config file:
```bash
NGE100 --config config.txt 
```
it is possible to set additional values behind the config file example:

```bash
NGE100 --config config.txt --fuse
```
## installing the package

### Option 1 
- build it yourself
```bash
git clone https://github.com/Faustan1000/Rhode-Schwarz-NGE100-Power-Supply
```
```bash
cd Rhode-Schwarz-NGE100-Power-Supply
```
```bash
python -m build 
```
```bash
pip install -e . 
```

### Option 2 
- download latest version directly
```bash
pip install https://github.com/Faustan1000/Rhode-Schwarz-NGE100-Power-Supply/releases/download/v0.1.2/rs_power_supply-0.1.2-py3-none-any.whl
```


