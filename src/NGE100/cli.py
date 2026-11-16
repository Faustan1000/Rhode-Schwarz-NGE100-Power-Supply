from .device import NGE100
import argparse
import sys
import shlex
import time
import logging

logger = logging.getLogger(__name__)

class _ChannelAction(argparse.Action):
    """--channel starts a new channel block; later options belong to it."""

    def __call__(self, parser, namespace, values, option_string=None):
        namespace.blocks.append({"channel": values})


class _BlockAction(argparse.Action):
    """Channel options (--volt, --curr, ...) are stored in the last block."""

    def __call__(self, parser, namespace, values, option_string=None):
        if not namespace.blocks:
            parser.error(f"{option_string} must come after --channel")
        if self.nargs == 0:
            values = self.const
        namespace.blocks[-1][self.dest] = values


def _block_flag(parser, name, help):
    parser.add_argument(name, action=_BlockAction, nargs=0, const=True, help=help)


def _build_parser():
    parser = argparse.ArgumentParser(
        description="Rhode&Schwarz NGE100 Power Supply Controls. "
                    "Repeat --channel to configure several channels in one call; "
                    "--volt/--curr/--on/--off/--fuse apply to the preceding --channel."
    )

    parser.add_argument("--config", help="Config file (.txt)")
    parser.add_argument("--resource",
                        help="VISA resource string (VISA Device ID, use --list to find)")
    parser.add_argument("--backend", help="VISA backend (e.g. @py)")
    parser.add_argument("--list", action="store_true", help="List VISA resources")

    parser.add_argument("--channel", type=int, action=_ChannelAction,
                        help="Select channel (can be given multiple times)")
    parser.add_argument("--volt", type=float, action=_BlockAction, help="Set voltage")
    parser.add_argument("--curr", type=float, action=_BlockAction, help="Set current")
    _block_flag(parser, "--on", "Turn output ON")
    _block_flag(parser, "--off", "Turn output OFF")
    _block_flag(parser, "--fuse", "Enable over-current shutdown")

    parser.add_argument("--measure", choices=["volt", "curr", "all"],
                        help="Measure voltage, current or all (all configured channels)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable debug logging")
    return parser


def _measure_line(psu, blocks, mode):
    parts = []
    for b in blocks:
        ch = b["channel"]
        psu.select_channel(ch)
        if mode == "volt":
            parts.append(f"CH{ch} | {float(psu.measure_voltage()):7.3f} V | "
                         f"Fuse: {psu.get_fuse_status():<10}")
        elif mode == "curr":
            parts.append(f"CH{ch} | {float(psu.measure_current()):7.3f} A | "
                         f"Fuse: {psu.get_fuse_status():<10}")
        else:
            v = psu.measure_all()
            parts.append(f"CH{ch} | {float(v['voltage']):7.3f} V | "
                         f"{float(v['current']):7.3f} A | Fuse: {v['fuse']:<10}")
    return "\r" + "  ||  ".join(parts)


def main():
    parser = _build_parser()

    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--config")
    config_args, _ = pre_parser.parse_known_args()

    argv = sys.argv[1:]
    if config_args.config:
        with open(config_args.config) as f:
            file_args = shlex.split(f.read(), comments=True)
        # Config file first, command line afterwards (cmd line options extend
        # or follow the channel blocks of the file).
        argv = file_args + argv

    args = parser.parse_args(argv, namespace=argparse.Namespace(blocks=[]))

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s"
    )
    if not args.verbose:
        # zeroconf logs scary tracebacks for unreachable network interfaces
        # during discovery, which are irrelevant for the user.
        logging.getLogger("zeroconf").setLevel(logging.ERROR)

    if args.list:
        sys.exit(0 if NGE100.list_resources(args.backend) else 1)

    if not args.resource:
        logger.error("--resource is required use --list to find available resources")
        sys.exit(1)

    if not args.blocks:
        logger.error("--channel is required")
        sys.exit(1)

    for b in args.blocks:
        if b.get("on") and b.get("off"):
            logger.error(f"CH{b['channel']}: --on and --off cannot be used together")
            sys.exit(1)

    psu = NGE100(args.resource, args.backend)

    try:
        psu.connect()

        for b in args.blocks:
            psu.select_channel(b["channel"])

            psu.set_fuse(
                state=bool(b.get("fuse")),
                current_limit=b.get("curr"),
                restore_output=bool(b.get("on"))
            )

            if (b.get("volt") is not None or b.get("curr") is not None
                    or b.get("on") or b.get("off")):
                psu.configure(
                    voltage=b.get("volt"),
                    current=b.get("curr"),
                    output=True if b.get("on") else False if b.get("off") else None
                )

        if args.measure:
            logger.info("Press Ctrl+C to stop")
            try:
                while True:
                    print(_measure_line(psu, args.blocks, args.measure),
                          end='', flush=True)
                    time.sleep(0.5)
            except KeyboardInterrupt:
                print()
                logger.info("Measurement stopped")

    except Exception as e:
        logger.error(e)

    finally:
        psu.close()


if __name__ == "__main__":
    main()
