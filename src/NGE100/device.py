import pyvisa
import logging

class NGE100:
    def __init__(self, resource_string, backend=None):
        self.resource_string = resource_string
        self.backend = backend
        self.rm = None
        self.instrument = None
        self.channel = 1  # default channel
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    @staticmethod
    def list_resources(backend=None):
        logger = logging.getLogger(__name__)
        try:
            rm = pyvisa.ResourceManager(backend) if backend else pyvisa.ResourceManager()
            resources = rm.list_resources()

            logger.info("Available VISA resources:")
            if resources:
                for r in resources:
                    logger.info(f"  - {r}")
            else:
                logger.info("  No resources found")

            rm.close()

        except Exception as e:
            logger.error(f"Error listing resources: {e}")

    def connect(self):
        try:
            if self.backend:
                self.rm = pyvisa.ResourceManager(self.backend)
                self.logger.debug(f"Using VISA backend: {self.backend}")
            else:
                self.rm = pyvisa.ResourceManager()
                self.logger.debug("Using default VISA backend")

            self.instrument = self.rm.open_resource(self.resource_string)
            self.instrument.write_termination = '\n'
            self.instrument.read_termination = '\n'
            self.instrument.timeout = 5000

            self.logger.info("Connected to power supply")
            self.logger.info("Trying IDN...")
            self.logger.info(self.instrument.query('*IDN?'))

        except Exception as e:
            raise RuntimeError(f"Connection failed: {e}")

    def select_channel(self, channel):
        if not self.instrument:
            raise RuntimeError("Not connected")

        self.channel = channel

        try:

            self.instrument.write(f'INST CH{channel}')
        except Exception:

            pass

    def configure(self, voltage=None, current=None, output=None):
        if not self.instrument:
            raise RuntimeError("Not connected")

        self.instrument.write(f'INST:NSEL {self.channel}')


        if voltage is not None:
            self.instrument.write(f'VOLT {voltage}')

        if current is not None:
            self.instrument.write(f'CURR {current}')

        if output is not None:
            self.instrument.write(f'OUTP {"ON" if output else "OFF"}')

    def measure_voltage(self):
        if not self.instrument:
            raise RuntimeError("Not connected")

        self.select_channel(self.channel)
        return self.instrument.query('MEAS:VOLT?').strip()

    def measure_current(self):
        if not self.instrument:
            raise RuntimeError("Not connected")

        self.select_channel(self.channel)
        return self.instrument.query('MEAS:CURR?').strip()

    def measure_all(self):
        if not self.instrument:
            raise RuntimeError("Not connected")

        self.select_channel(self.channel)

        voltage = self.instrument.query('MEAS:VOLT?').strip()
        current = self.instrument.query('MEAS:CURR?').strip()
        fuse = self.get_fuse_status()

        return {
            "voltage": voltage,
            "current": current,
            "fuse": fuse
        }
    def get_fuse_status(self):
        if not self.instrument:
            raise RuntimeError("Not connected")

        self.instrument.write(f'INST:NSEL {self.channel}')

        enabled = self.instrument.query('FUSE:STAT?').strip()
        tripped = self.instrument.query('FUSE:TRIP?').strip()

        if tripped == '1':
            return "TRIGGERED"
        elif enabled == '1':
            return "ENABLED"
        else:
            return "DISABLED"

    def set_fuse(self, state: bool, current_limit=None, restore_output=False):
        if not self.instrument:
            raise RuntimeError("Not connected")

        self.instrument.write(f'INST:NSEL {self.channel}')

        prev_out = self.instrument.query('OUTP?').strip()

        if state:

            if prev_out == '1':
                self.instrument.write('OUTP OFF')

            if current_limit is not None:
                self.instrument.write(f'FUSE:CURR {current_limit}')

            self.instrument.write('FUSE:STAT ON')


            if restore_output or prev_out == '1':
                self.instrument.write('OUTP ON')

        else:
            self.instrument.write('OUTP OFF')
            self.instrument.write('FUSE:CLE')
            self.instrument.write('FUSE:STAT OFF')

            if prev_out == '1':
                self.instrument.write('OUTP ON')


    def fuse_tripped(self):
        return self.instrument.query('FUSE:TRIP?').strip()

    def reset_fuse(self):
        self.instrument.write('FUSE:CLE')

    def close(self):
        if self.instrument:
            self.instrument.close()
        if self.rm:
            self.rm.close()