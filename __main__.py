import sys
from valhalla.main import start


def _print_help():
    msg = (
        "🌌 valhalla is a toolkit designed to streamline the release of new versions of software. 🌌\n"
        "\n"
        "Usage:\n"
        "  valhalla            Start the release process (same as 'valhalla start').\n"
        "  valhalla start      Start the release process.\n"
        "  valhalla -h, --help Show this help and exit.\n"
        "\n"
        "Docs: https://logchange.dev/tools/valhalla/\n"
        "\n"
        "Notes:\n"
        "- The 'valhalla' command starts the process by detecting the release version,\n"
        "  reading configuration (valhalla.yml), creating a release and optionally a\n"
        "  merge request.\n"
        "- You can also provide the 'start' subcommand, which does exactly the same as\n"
        "  running 'valhalla' without arguments.\n"
    )
    print(msg)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        # Default behavior: start the process
        start()
        return

    if argv[0] in ("-h", "--help"):
        _print_help()
        return

    if argv[0] == "start":
        start()
        return

    # Unknown command -> print help and exit with error
    _print_help()
    sys.exit(1)


if __name__ == '__main__':
    main()
