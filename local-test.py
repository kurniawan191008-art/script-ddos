#!/usr/bin/env python3

-- coding: utf-8 --

"""
LocalStorm - HTTP Load Tester for Local Networks
Optimized for Termux/Android. Private IP only.
"""

import argparse
import collections
import concurrent.futures
import ipaddress
import signal
import sys
import threading
import time
import urllib.parse
from typing import Deque, Dict, Optional, Tuple

import requests

======================== STATISTICS ========================

class Stats:
"""Thread-safe rolling statistics collector."""

def __init__(self, max_latency_samples: int = 1000):  
    self.lock = threading.Lock()  
    self.total_requests: int = 0  
    self.successful: int = 0  
    self.failed: int = 0  
    self.total_bytes: int = 0  
    self.latencies: Deque[float] = collections.deque(  
        maxlen=max_latency_samples  
    )  
    self.errors: Dict[str, int] = {  
        "timeout": 0,  
        "connection": 0,  
        "http": 0,  
        "other": 0,  
    }  
    self.start_time: float = 0.0  

def record_success(self, elapsed: float, bytes_received: int) -> None:  
    with self.lock:  
        self.total_requests += 1  
        self.successful += 1  
        self.total_bytes += bytes_received  
        self.latencies.append(elapsed)  

def record_failure(self, error_type: str, elapsed: float) -> None:  
    with self.lock:  
        self.total_requests += 1  
        self.failed += 1  
        self.errors[error_type] = self.errors.get(error_type, 0) + 1  
        # Still record latency for failures (timeouts count as long timeout)  
        self.latencies.append(elapsed)  

def get_snapshot(self) -> dict:  
    with self.lock:  
        elapsed = time.monotonic() - self.start_time  
        rps = self.total_requests / elapsed if elapsed > 0 else 0  

        sorted_latencies = sorted(self.latencies)  
        p95 = 0.0  
        max_lat = 0.0  
        avg_lat = 0.0  
        count = len(sorted_latencies)  
        if count > 0:  
            avg_lat = sum(sorted_latencies) / count  
            p95 = sorted_latencies[int(count * 0.95)]  
            max_lat = sorted_latencies[-1]  

        return {  
            "total": self.total_requests,  
            "success": self.successful,  
            "failed": self.failed,  
            "bytes": self.total_bytes,  
            "rps": rps,  
            "avg_lat": avg_lat * 1000,  # convert to ms  
            "p95_lat": p95 * 1000,  
            "max_lat": max_lat * 1000,  
            "errors": self.errors.copy(),  
            "elapsed": elapsed,  
        }

======================== VALIDATOR ========================

def is_target_allowed(url: str) -> Tuple[bool, str]:
"""
Validate that target is localhost or private IPv4.
Returns (is_allowed, reason).
"""
try:
parsed = urllib.parse.urlparse(url)
host = parsed.hostname
if not host:
return False, "Invalid URL: missing hostname."

# Handle localhost aliases  
    if host.lower() == "localhost" or host == "127.0.0.1":  
        return True, "localhost"  

    # Try to parse as IP address  
    try:  
        ip = ipaddress.ip_address(host)  
        if ip.is_private:  
            return True, f"private IP ({ip})"  
        return False, f"public IP ({ip}) is not allowed (must be private)."  
    except ValueError:  
        # Hostname like 'my-server.local' – we block it for safety,  
        # unless user explicitly forces (but we don't implement force for safety).  
        return False, (  
            f"Hostname '{host}' cannot be resolved to a private IP. "  
            "Please use IP address or 'localhost'."  
        )  
except Exception as e:  
    return False, f"Validation error: {e}"

======================== WORKER ========================

def worker_task(
url: str,
timeout: float,
stats: Stats,
stop_event: threading.Event,
rps_share: float,
) -> None:
"""
Single worker loop. Uses a persistent Session for connection pooling.
"""
session = requests.Session()
session.headers.update({"User-Agent": "LocalStorm-LoadTest/1.0"})

# Rate limiting calculation  
sleep_interval = 1.0 / rps_share if rps_share > 0 else 0.0  

while not stop_event.is_set():  
    start_time = time.monotonic()  
    try:  
        response = session.get(url, timeout=timeout)  
        elapsed = time.monotonic() - start_time  
        content_length = len(response.content)  

        # Consider 2xx/3xx as success, 4xx/5xx as HTTP error  
        if 200 <= response.status_code < 400:  
            stats.record_success(elapsed, content_length)  
        else:  
            stats.record_failure("http", elapsed)  

    except requests.exceptions.Timeout:  
        elapsed = time.monotonic() - start_time  
        stats.record_failure("timeout", elapsed)  
    except requests.exceptions.ConnectionError:  
        elapsed = time.monotonic() - start_time  
        stats.record_failure("connection", elapsed)  
    except Exception:  
        elapsed = time.monotonic() - start_time  
        stats.record_failure("other", elapsed)  

    # Enforce rate limit  
    if sleep_interval > 0:  
        time.sleep(max(0.0, sleep_interval - (time.monotonic() - start_time)))

======================== STATS PRINTER ========================

def stats_printer(stats: Stats, stop_event: threading.Event) -> None:
"""Print real-time statistics every second."""
while not stop_event.is_set():
time.sleep(1.0)
if stats.total_requests == 0:
continue

s = stats.get_snapshot()  
    print(  
        f"\r[Stats] Total: {s['total']} | "  
        f"OK: {s['success']} | Fail: {s['failed']} | "  
        f"RPS: {s['rps']:.1f} | "  
        f"Latency (ms) Avg: {s['avg_lat']:.1f} P95: {s['p95_lat']:.1f} Max: {s['max_lat']:.1f} | "  
        f"Bytes: {s['bytes']/1024:.1f}KB   ",  
        end="",  
        flush=True,  
    )

======================== SIGNAL HANDLER ========================

def signal_handler(stop_event: threading.Event) -> None:
"""Handle SIGINT (Ctrl+C) gracefully."""
def handler(sig, frame):
print("\n[!] SIGINT received. Shutting down gracefully...")
stop_event.set()

signal.signal(signal.SIGINT, handler)

======================== MAIN ========================

def main() -> None:
parser = argparse.ArgumentParser(
description="LocalStorm - HTTP Load Tester for local/private networks."
)
parser.add_argument(
"url", help="Target URL (e.g., http://192.168.1.100:8080)"
)
parser.add_argument(
"--duration",
type=int,
default=10,
help="Test duration in seconds (default: 10).",
)
parser.add_argument(
"--workers",
type=int,
default=4,
help="Number of concurrent workers (default: 4).",
)
parser.add_argument(
"--rps",
type=int,
default=10,
help="Maximum total requests per second (default: 10).",
)
parser.add_argument(
"--timeout",
type=float,
default=5.0,
help="Request timeout in seconds (default: 5.0).",
)

args = parser.parse_args()  

# 1. Validate target  
allowed, reason = is_target_allowed(args.url)  
if not allowed:  
    print(f"[ERROR] Target rejected: {reason}")  
    sys.exit(1)  
print(f"[+] Target allowed: {args.url} ({reason})")  

# 2. Sanity check duration  
if args.duration <= 0:  
    print("[ERROR] --duration must be positive.")  
    sys.exit(1)  
if args.rps <= 0:  
    print("[ERROR] --rps must be positive.")  
    sys.exit(1)  
if args.workers <= 0:  
    print("[ERROR] --workers must be positive.")  
    sys.exit(1)  

# 3. Setup  
stats = Stats()  
stats.start_time = time.monotonic()  
stop_event = threading.Event()  

# 4. Signal handler  
signal_handler(stop_event)  

# 5. Launch stats printer thread  
printer_thread = threading.Thread(  
    target=stats_printer, args=(stats, stop_event), daemon=True  
)  
printer_thread.start()  

# 6. Launch worker pool  
rps_per_worker = args.rps / args.workers  
print(  
    f"[+] Starting load test: duration={args.duration}s, "  
    f"workers={args.workers}, rps={args.rps}, timeout={args.timeout}s"  
)  
print("[+] Press Ctrl+C to stop early.\n")  

with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:  
    futures = []  
    for _ in range(args.workers):  
        future = executor.submit(  
            worker_task,  
            args.url,  
            args.timeout,  
            stats,  
            stop_event,  
            rps_per_worker,  
        )  
        futures.append(future)  

    # 7. Run for specified duration  
    try:  
        time.sleep(args.duration)  
    except KeyboardInterrupt:  
        pass  # Handled by signal handler  

    # 8. Stop workers  
    stop_event.set()  

    # 9. Wait for workers to finish gracefully (with timeout)  
    for future in concurrent.futures.as_completed(futures, timeout=5.0):  
        try:  
            future.result()  
        except concurrent.futures.TimeoutError:  
            print("[!] Some workers did not finish in time, forcing exit.")  
            break  
        except Exception as e:  
            print(f"[!] Worker error: {e}")  

# 10. Final summary  
print("\n\n" + "=" * 50)  
print(" LOAD TEST COMPLETED")  
print("=" * 50)  
final_stats = stats.get_snapshot()  
print(f"Total Duration      : {final_stats['elapsed']:.2f}s")  
print(f"Total Requests      : {final_stats['total']}")  
print(f"Successful          : {final_stats['success']}")  
print(f"Failed              : {final_stats['failed']}")  
print(f"Requests/sec (avg)  : {final_stats['rps']:.2f}")  
print(f"Total Data Transferred: {final_stats['bytes'] / 1024:.2f} KB")  
print(f"\nLatency (ms):")  
print(f"  Average           : {final_stats['avg_lat']:.2f}")  
print(f"  P95               : {final_stats['p95_lat']:.2f}")  
print(f"  Maximum           : {final_stats['max_lat']:.2f}")  
print(f"\nError Breakdown:")  
for err_type, count in final_stats["errors"].items():  
    if count > 0:  
        print(f"  {err_type.capitalize()}: {count}")  
print("=" * 50)

if name == "main":
main()