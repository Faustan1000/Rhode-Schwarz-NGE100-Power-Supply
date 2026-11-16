# Python Package for R&S NGE102B / 103B series Power supply
Tested on NGE102B but probably also works on NGE103B 
![](https://assets.rohde-schwarz.com/public/image/products/test-and-measurement/powersupplies/dc-powersupplies/dc-powersupplies-hardware/nge100b//rs-nge100b-powersupply-series-front-low-rohde-schwarz_200_66630_1024_576_1.jpg)
## How 2 use

after installing the package and activating an environment:

### Use as a python lib
install the package in your environment
```bash
pip install https://github.com/Faustan1000/Rhode-Schwarz-NGE100-Power-Supply/releases/download/v0.1.3/rs_power_supply-0.1.3-py3-none-any.whl
```
example:
```bash
from NGE100 import NGE100

# VISA resource string of the power supply
RESOURCE = "USB0::2733::407::<serial>::0::INSTR"  # find yours with: NGE100 --list

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

#### Using two channels (CH1 and CH2)
The channel is selected with `select_channel()`. Configure the channels one after the other:
```python
from NGE100 import NGE100

RESOURCE = "USB0::2733::407::<serial>::0::INSTR"

with NGE100(RESOURCE) as psu:
    for channel, volt in ((1, 12.0), (2, 24.0)):
        psu.select_channel(channel)
        psu.set_fuse(state=True, current_limit=1.0)
        psu.configure(voltage=volt, current=1.0, output=True)

    # read back both channels
    for channel in (1, 2):
        psu.select_channel(channel)
        print(f"CH{channel}:", psu.measure_all())
```
### Use as a Cli tool
- create a venv
```bash
python -m venv .venv
```
- install package 
```bash
pip install https://github.com/Faustan1000/Rhode-Schwarz-NGE100-Power-Supply/releases/download/v0.1.3/rs_power_supply-0.1.3-py3-none-any.whl
```
find resources:
```bash
NGE100 --list
```

Control the Power Supply (example)
```bash
NGE100 --channel 1 --volt 5 --curr 1 --off --fuse --measure all --resource USB0::----::INSTR
```
Control two channels in one call (channel 1 and 2 at the same time):
```bash
NGE100 --resource USB0::----::INSTR --channel 1 --volt 12 --curr 1 --on --fuse --channel 2 --volt 24 --curr 1 --on --fuse --measure all
```
available arguments:
- list : lists all available Devices
- channel : selects a channel, can be given several times (e.g. `--channel 1 ... --channel 2 ...`)
- volt : selects voltage (applies to the preceding `--channel`)
- curr : selects maximum current (applies to the preceding `--channel`)
- on/off : switches on/off the channel (applies to the preceding `--channel`)
- fuse : switches on the fuse option on the NGE10xB (applies to the preceding `--channel`)
- measure : `volt`, `curr` or `all`, shows the values of all given channels in one line
- resource : selects a VISA resource connected to the pc (use `--list` to find it)
- backend : optional VISA backend (default: automatic, e.g. `@py`)
- config : selects a config file which can define all parameters listed here
- verbose (`-v`) : enable debug logging

Note: `--volt`, `--curr`, `--on`, `--off` and `--fuse` must come after the `--channel` they belong to.
`--on` and `--off` cannot be combined for the same channel.

### (Option) config file

instead of typing in all arguments by itself there is also the option to create a config file which contains all information

a config file can contain one or more channels. Every option belongs to the `--channel` above it, lines starting with `#` are comments.

example file (config.txt) with one channel
```bash
--channel 1
--volt 5
--curr 1
--off
--resource USB0::----::INSTR
```

example file with two channels (config_2ch.txt)
```bash
--resource USB0::----::INSTR

# channel 1: 12 V / 1 A
--channel 1
--volt 12
--curr 1
--off
--fuse

# channel 2: 24 V / 1 A
--channel 2
--volt 24
--curr 1
--off
--fuse
```

Use the config file:
```bash
NGE100 --config config.txt 
```
options given on the command line are appended after the config file. Therefore they apply to the **last** channel of the file:

```bash
NGE100 --config config.txt --fuse
```
Use `--measure all` the same way to display all channels of the file.

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
pip install build && python -m build
```
```bash
pip install -e . 
```

### Option 2 
- download latest version directly
```bash
pip install https://github.com/Faustan1000/Rhode-Schwarz-NGE100-Power-Supply/releases/download/v0.1.3/rs_power_supply-0.1.3-py3-none-any.whl
```

## Continuous integration

A GitHub Actions workflow (`.github/workflows/ci.yml`) installs the package on Linux, Windows and macOS and runs `NGE100 --list`.
It fails on any error or traceback. No real power supply is switched there, the check only makes sure that the package installs and starts.

## Linux: USB access

The package uses the pure-python `pyvisa-py` backend (installed automatically), so no NI-VISA is needed.
On Linux, USB devices are only writable by `root` by default. Without permission the power supply is **not listed** by `NGE100 --list`, or it shows up as `USB0::...::???::0::INSTR` together with the warning
`User does not have permission to write to /dev/bus/usb/...`.

Fix it once per computer with a udev rule (your user must be member of the group used in the rule, `plugdev` here):

```bash
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="0aad", MODE="0660", GROUP="plugdev"' | sudo tee /etc/udev/rules.d/99-rs-nge.rules
```
```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

Then unplug and replug the power supply and check:

```bash
NGE100 --list
```

The device should appear as `USB0::2733::407::<serial>::0::INSTR`. Use this string with `--resource`.

If your user is not in `plugdev`, add it with `sudo usermod -aG plugdev $USER` and log in again.

