
# -*- coding: utf-8 -*-
import argparse
import sys
import logging
from contextlib import ExitStack, redirect_stdout, redirect_stderr
from pathlib import Path

# Import the user's converter module (must expose main())
from . import converter as _converter

class Tee:
    """A tiny file-like wrapper that tees writes to multiple streams."""
    def __init__(self, *streams):
        self.streams = streams
    def write(self, b):
        for s in self.streams:
            s.write(b)
    def flush(self):
        for s in self.streams:
            s.flush()

def run(argv=None):
    parser = argparse.ArgumentParser(
        prog="olca2tidas",
        description="Wraps the openLCA JSON-LD → TIDAS/eILCD converter as an easy CLI with logging."
    )
    # Logging options handled by this wrapper
    parser.add_argument("--log-file", default=None, help="Write console output to a log file (in addition to the console).")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set logging/verbosity level for this wrapper (default: INFO)."
    )
    # Everything after '--' (or unknown flags) will be forwarded to the underlying converter
    parser.add_argument("converter_args", nargs=argparse.REMAINDER, help="Arguments forwarded to the underlying converter script. Use '-- --help' to see them.")
    args = parser.parse_args(argv)

    # Configure simple logging for this wrapper
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    logger = logging.getLogger("olca2tidas")

    # If the user wants help for the underlying converter, allow `olca2tidas -- --help`
    if args.converter_args and args.converter_args[0] == "--" and len(args.converter_args) == 2 and args.converter_args[1] in ("-h", "--help"):
        # Re-run the converter's argparse by invoking its main with sys.argv set
        sys.argv = ["converter", args.converter_args[1]]
        return _converter.main()

    # Prepare to forward all remaining args (after optional '--') to converter
    forward = []
    if args.converter_args:
        forward = args.converter_args
        if forward and forward[0] == "--":
            forward = forward[1:]

    logger.debug("Forwarding args to converter: %s", forward)

    # Run converter.main() with stdout/stderr optionally teed to a log file
    with ExitStack() as stack:
        if args.log_file:
            log_path = Path(args.log_file).expanduser().resolve()
            log_path.parent.mkdir(parents=True, exist_ok=True)
            f = open(log_path, "w", encoding="utf-8")
            stack.enter_context(f)
            stack.enter_context(redirect_stdout(Tee(sys.stdout, f)))
            stack.enter_context(redirect_stderr(Tee(sys.stderr, f)))
            logger.info("Logging console output to %s", log_path)

        # Now call the user's converter main() as-is
        # It will parse its own arguments and run its pipeline.
        if forward:
            sys.argv = ["converter"] + forward
        else:
            sys.argv = ["converter"]
        return _converter.main()

if __name__ == "__main__":
    sys.exit(run())
