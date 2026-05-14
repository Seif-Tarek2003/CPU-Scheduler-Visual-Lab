"""
Process model and input-file loader.
"""

from __future__ import annotations
import copy
from dataclasses import dataclass, field
from typing import List


@dataclass
class Process:
    pid:          str
    arrival_time: int
    burst_time:   int
    remaining:    int = field(init=False)  # for preemptive algorithms
    start_time:   int = field(default=-1, init=False)
    finish_time:  int = field(default=-1, init=False)

    def __post_init__(self):
        self.remaining = self.burst_time

    # ── Derived metrics (filled after scheduling) ─────────────────────────
    @property
    def turnaround_time(self) -> int:
        return self.finish_time - self.arrival_time

    @property
    def waiting_time(self) -> int:
        return self.turnaround_time - self.burst_time

    def reset(self) -> "Process":
        """Return a fresh copy suitable for re-scheduling."""
        return copy.copy(Process(self.pid, self.arrival_time, self.burst_time))


def load_processes(filename: str) -> List[Process]:
    """
    Parse an input file where each line is:
        <process_id>  <arrival_time>  <burst_time>
    Lines starting with '#' and blank lines are ignored.
    """
    processes: List[Process] = []
    with open(filename) as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 3:
                raise ValueError(f"Malformed line: '{raw.rstrip()}'")
            pid, arrival, burst = parts[0], int(parts[1]), int(parts[2])
            processes.append(Process(pid, arrival, burst))
    return processes
