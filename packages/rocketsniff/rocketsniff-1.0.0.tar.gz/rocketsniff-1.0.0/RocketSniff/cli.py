import argparse
from .core import get_server_ip

def main():
    parser = argparse.ArgumentParser(
        prog="RocketSniff",
        description="Find the current Rocket League server IP and port."
    )
    parser.add_argument(
        "-t", "--timeout", type=float, default=10.0,
        help="Max seconds to wait for a server IP (default: 10)"
    )

    args = parser.parse_args()

    ip_port = get_server_ip(timeout=args.timeout)
    if ip_port:
        print(f"Rocket League Server: {ip_port}")
    else:
        print("No server found within timeout.")
