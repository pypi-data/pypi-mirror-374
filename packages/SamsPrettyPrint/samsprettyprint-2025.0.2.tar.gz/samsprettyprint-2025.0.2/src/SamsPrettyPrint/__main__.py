import argparse
from . import print_title, print_table
import pyperclip


def main(argv=None):
    """
    Console script for SamsPrettyPrint.
    """
    parser = argparse.ArgumentParser(
        prog="spp",
        description="Pretty-print titles and tables in the console."
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Text to be prettified."
    )

    parser.add_argument(
        "--format", "-f",
        choices=['1', '3', '5'],
        default='3',
        help="Output level (default: '3')."
    )

    parser.add_argument(
        "--prefix", "-p",
        default='%',
        help="The prefix gets printed before every line (default: '%')."
    )

    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Print the version of SamsPrettyPrint and exit."
    )

    args = parser.parse_args(argv)

    # Handle version
    if args.version:
        from . import __version__
        print(f"SamsPrettyPrint {__version__}")
        return

    # Handle input
    if args.input:
        print_title(
            args.input,
            level=int(args.format),
            prefix=args.prefix + ' ',
            copy_to_clipboard=True
        )


if __name__ == '__main__':
    main()
