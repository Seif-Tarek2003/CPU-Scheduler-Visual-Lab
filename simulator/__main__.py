"""
CPU Scheduler Simulator — Entry Point
Usage: python -m simulator <input_file> [--algo fcfs|rr|sjf|srtf] [--quantum N]

Input file format (one process per line):
    <process_id> <arrival_time> <burst_time>
"""

import sys
import os
import argparse

from simulator.process import load_processes
from simulator.schedulers.fcfs  import FCFS
from simulator.schedulers.rr    import RR
from simulator.schedulers.sjf   import SJF
from simulator.schedulers.srtf  import SRTF


SCHEDULERS = {
    "fcfs": FCFS,
    "rr":   RR,
    "sjf":  SJF,
    "srtf": SRTF,
}


def main():
    parser = argparse.ArgumentParser(description="CPU Scheduler Simulator")
    parser.add_argument("filename",            help="Input file with process definitions")
    parser.add_argument("--algo",   default="all",
                        choices=["fcfs", "rr", "sjf", "srtf", "all"],
                        help="Scheduling algorithm (default: all)")
    parser.add_argument("--quantum", type=int, default=2,
                        help="Time quantum for Round Robin (default: 2)")
    args = parser.parse_args()

    if not os.path.exists(args.filename):
        print(f"Error: file '{args.filename}' not found.")
        sys.exit(1)

    processes = load_processes(args.filename)
    os.makedirs("schedules", exist_ok=True)

    algos = list(SCHEDULERS.keys()) if args.algo == "all" else [args.algo]

    for name in algos:
        cls = SCHEDULERS[name]
        kwargs = {"quantum": args.quantum} if name == "rr" else {}
        scheduler = cls(processes, **kwargs)
        scheduler.run()
        print(f"[{name.upper()}] Average waiting time: {scheduler.average_waiting_time():.2f}")


if __name__ == "__main__":
    main()
