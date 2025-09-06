import argparse
import time
from .core import get_server_ip, ServerWatcher

def main():
    parser = argparse.ArgumentParser(
        prog="RocketSniff",
        description="Find the current Rocket League server IP and port."
    )
    parser.add_argument(
        "-t", "--timeout", type=float, default=10.0,
        help="Max seconds to wait for a server IP (default: 10)"
    )
    parser.add_argument(
        "-w", "--watch", action="store_true",
        help="Watch logs in real-time and print new server IPs as they appear"
    )

    args = parser.parse_args()

    if args.watch:
        print("Watching Rocket League logs for new servers... Press Ctrl+C to stop.")
        def callback(ip_port):
            print(f"New server detected: {ip_port}")

        watcher = ServerWatcher(callback=callback)
        watcher.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            watcher.stop()
            print("Stopped watching.")
    else:
        ip_port = get_server_ip(timeout=args.timeout)
        if ip_port:
            print(f"Rocket League Server: {ip_port}")
        else:
            print("No server found within timeout.")
