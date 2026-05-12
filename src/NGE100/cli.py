from .device import NGE100
import argparse
import sys
import shlex
import time
import logging

logger = logging.getLogger(__name__)

def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--config")

    config_args, remaining_argv = pre_parser.parse_known_args()

    parser = argparse.ArgumentParser(description="Rhode&Schwarz NGE100 Power Supply Controls")

    parser.add_argument("--config", help="Config file (.txt)")
    parser.add_argument("--resource",
                        help="VISA resource string (VISA Device ID, use --list to find)")

    parser.add_argument("--backend", help="VISA backend (e.g. @py)")
    parser.add_argument("--list", action="store_true", help="List VISA resources")

    parser.add_argument("--channel", type=int,
                        help="Select channel")

    parser.add_argument("--volt", type=float, help="Set voltage")
    parser.add_argument("--curr", type=float, help="Set current")
    parser.add_argument("--on", action="store_true", help="Turn output ON")
    parser.add_argument("--off", action="store_true", help="Turn output OFF")

    parser.add_argument("--measure", choices=["volt", "curr", "all"],
                        help="Measure voltage, current or all (per channel)")

    parser.add_argument("--fuse", action="store_true",
                        help="Enable over-current shutdown")

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging"
    )

    if config_args.config:
        with open(config_args.config) as f:
            file_args = shlex.split(f.read())

        args = parser.parse_args(file_args + remaining_argv)

    else:
        args = parser.parse_args()

    if args.list:
        NGE100.list_resources(args.backend)
        return

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    if not args.resource:
        logger.error("--resource is required use --list to find available resources")
        sys.exit(1)

    """if the list option is not used check if a channel was given """
    if not args.list and not args.channel:
        logger.error("--channel is required")
        sys.exit(1)

    psu = NGE100(args.resource, args.backend)

    try:
        psu.connect()

        # Channel setzen
        psu.select_channel(args.channel)

        psu.set_fuse(
            state=args.fuse,
            current_limit=args.curr,
            restore_output=args.on
        )

        if args.volt or args.curr or args.on or args.off:
            psu.configure(
                voltage=args.volt,
                current=args.curr,
                output=True if args.on else False if args.off else None
            )

        if args.measure == "volt":
            voltage = psu.measure_voltage()
            fuse = psu.get_fuse_status()

            logger.info(f"Measured voltage (CH{args.channel}): {voltage} V")
            logger.info(f"Fuse status: {fuse}")

        if args.measure:

            logger.info("Press Ctrl+C to stop")

            try:

                while True:

                    if args.measure == "volt":

                        voltage = psu.measure_voltage()

                        fuse = psu.get_fuse_status()

                        line = (

                            f"\rCH{args.channel} | "

                            f"{float(voltage):7.3f} V | "

                            f"Fuse: {fuse:<10}"

                        )


                    elif args.measure == "curr":

                        current = psu.measure_current()

                        fuse = psu.get_fuse_status()

                        line = (

                            f"\rCH{args.channel} | "

                            f"{float(current):7.3f} A | "

                            f"Fuse: {fuse:<10}"

                        )


                    elif args.measure == "all":

                        values = psu.measure_all()

                        line = (

                            f"\rCH{args.channel} | "

                            f"{float(values['voltage']):7.3f} V | "

                            f"{float(values['current']):7.3f} A | "

                            f"Fuse: {values['fuse']:<10}"

                        )

                    print(line, end='', flush=True)

                    time.sleep(0.5)


            except KeyboardInterrupt:

                logger.info("\nMeasurement stopped")



    except Exception as e:
        logger.error(e)

    finally:
        psu.close()


if __name__ == "__main__":
    main()