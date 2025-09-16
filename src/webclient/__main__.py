import argparse

from webclient import HTTPWebClient

DEFAULT_HOST = "www.example.com"
DEFAULT_PORT = 80
DEFAULT_PATH = "/"

DEFAULT_OUTPUT_FILE = "./webout"


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "host",
        nargs="?",
        default=DEFAULT_HOST,
        help="Hostname of the server to connect to (default: %(default)s)",
    )
    parser.add_argument(
        "port",
        nargs="?",
        type=int,
        default=DEFAULT_PORT,
        help="Port number to connect to (default: %(default)s)",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=DEFAULT_PATH,
        help="Path to request from the server (default: %(default)s)",
    )
    parser.add_argument(
        "-f",
        "--file",
        default=DEFAULT_OUTPUT_FILE,
        help="Output file to save the response (default: %(default)s)",
    )
    parser.add_argument(
        "-nf",
        "--no-file",
        action="store_true",
        help="Do not save output to a file",
    )
    args = parser.parse_args()
    server_host = args.host
    server_port = args.port
    server_path = args.path
    output_file = args.file
    no_file = args.no_file

    client = HTTPWebClient(server_host, server_port, server_path)
    client.get(output_file if not no_file else None)


if __name__ == "__main__":
    main()
