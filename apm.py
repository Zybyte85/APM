import argparse
import funcs
import consts


def _get_parser() -> argparse.ArgumentParser:
    """Returns CLI parser.

    Returns:
        argparse.ArgumentParser: Created parser.
    """
    parser = argparse.ArgumentParser(
        prog="apm",
        epilog="Please report bugs at https://github.com/Zybyte85/APM",
    )

    subparsers = parser.add_subparsers(dest="command")

    install_parser = subparsers.add_parser("install")
    install_parser.add_argument(
        "app_name",
        type=str,
        help="Adds an Appimage from the repository or Github repository",
        metavar="<app name or user/repo>",
    )

    remove_parser = subparsers.add_parser("remove")
    remove_parser.add_argument(
        "app_name",
        type=str,
        help="Remove the app from your system",
        metavar="<app name or user/repo>",
    )

    return parser


def main():
    parser = _get_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
    elif args.command == "install":
        funcs.install(args.app_name)
    elif args.command == "remove":
        funcs.remove(args.app_name)


if __name__ == "__main__":
    consts.make_path()
    main()
