# Python Package for R&S NGE102B / 103B series Power supply
Tested on NGE102B but probably also works on NGE103B 
![](https://assets.rohde-schwarz.com/public/image/products/test-and-measurement/powersupplies/dc-powersupplies/dc-powersupplies-hardware/nge100b//rs-nge100b-powersupply-series-front-low-rohde-schwarz_200_66630_1024_576_1.jpg)
## How 2 use

after installing the package and activating an environment:

### Use as a python lib

### Use as a Cli tool
- create a venv
```bash
python -m venv .venv
```
- install package 
```bash
pip install https://github.com/Faustan1000/Rhode-Schwarz-NGE100-Power-Supply/releases/download/v0.1.0/rs_power_supply-0.1.0-py3-none-any.whl
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
pip install https://github.com/Faustan1000/Rhode-Schwarz-NGE100-Power-Supply/releases/download/v0.1.0/rs_power_supply-0.1.0-py3-none-any.whl
```


