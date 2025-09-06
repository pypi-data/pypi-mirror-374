import os
import re
import time
import threading
from typing import Optional, Callable, Generator, Tuple

# Paths to Rocket League logs
LOG_PATHS = [
    os.path.expanduser("~\\Documents\\My Games\\Rocket League\\TAGame\\Logs\\Launch.log"),
    os.path.expanduser("~\\AppData\\Local\\Rocket League\\Saved\\Logs\\Launch.log")
]

# Regex to capture server IP:Port
IP_REGEX = re.compile(r'GameURL="([\d\.]+):(\d+)"')


def follow_log(path: str) -> Generator[str, None, None]:
    """Yield new lines from a log file."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.01)
                    continue
                yield line
    except FileNotFoundError:
        return
    except Exception:
        return


def find_server_ip() -> Optional[str]:
    """Return the latest Rocket League server IP:port or None if not found."""
    generators = [follow_log(path) for path in LOG_PATHS]

    while True:
        for gen in generators:
            try:
                line = next(gen)
            except StopIteration:
                continue
            match = IP_REGEX.search(line)
            if match:
                ip, port = match.group(1), match.group(2)
                return f"{ip}:{port}"
        time.sleep(0.05)


def get_server_ip(timeout: float = 10.0) -> Optional[str]:
    """
    Get the Rocket League server IP within a timeout.
    
    :param timeout: Max seconds to wait for a server IP
    :return: server IP:port or None
    """
    start = time.time()
    while True:
        ip_port = find_server_ip()
        if ip_port:
            return ip_port
        if time.time() - start > timeout:
            return None
        time.sleep(0.05)


class ServerWatcher:
    """
    Watch Rocket League logs for server IP changes in real-time.
    Call `callback(ip_port)` whenever a new server is detected.
    """

    def __init__(self, callback: Callable[[str], None], poll_interval: float = 0.5):
        self.callback = callback
        self.poll_interval = poll_interval
        self.last_ip_port: Optional[str] = None
        self._thread = threading.Thread(target=self._watch, daemon=True)
        self._stop = threading.Event()

    def start(self):
        """Start watching in a background thread."""
        self._stop.clear()
        self._thread.start()

    def stop(self):
        """Stop watching."""
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join(timeout=1)

    def _watch(self):
        generators = [follow_log(path) for path in LOG_PATHS]
        while not self._stop.is_set():
            updated = False
            for gen in generators:
                try:
                    line = next(gen)
                except StopIteration:
                    continue
                match = IP_REGEX.search(line)
                if match:
                    ip_port = f"{match.group(1)}:{match.group(2)}"
                    if ip_port != self.last_ip_port:
                        self.last_ip_port = ip_port
                        updated = True
            if updated:
                self.callback(self.last_ip_port)
            time.sleep(self.poll_interval)
