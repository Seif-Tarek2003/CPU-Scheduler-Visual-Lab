"""
Abstract base class for all CPU schedulers.
"""

from __future__ import annotations
import os
import copy
from abc import ABC, abstractmethod
from typing import List, Tuple

from simulator.process import Process


class BaseScheduler(ABC):
    """
    Subclasses implement `perform_schedule` and call:
        self.context_switch(timestamp, pid)
    every time the CPU switches to a new process.
    """

    name: str = "base"

    def __init__(self, processes: List[Process]):
        # Deep-copy so each scheduler gets its own mutable state
        self.processes: List[Process] = [
            copy.copy(Process(p.pid, p.arrival_time, p.burst_time))
            for p in processes
        ]
        self._log: List[Tuple[int, str]] = []   # (timestamp, pid)

    # ── Public API ────────────────────────────────────────────────────────
    def run(self) -> None:
        self._log.clear()
        self.perform_schedule()
        self._write_output()

    def context_switch(self, timestamp: int, pid: str) -> None:
        """Call every time the CPU is assigned to a new process."""
        self._log.append((timestamp, pid))

    def average_waiting_time(self) -> float:
        waits = [p.waiting_time for p in self.processes if p.finish_time != -1]
        return sum(waits) / len(waits) if waits else 0.0

    # ── To be implemented ─────────────────────────────────────────────────
    @abstractmethod
    def perform_schedule(self) -> None:
        """Run the scheduling simulation and populate process metrics."""

    # ── Output ────────────────────────────────────────────────────────────
    def _write_output(self) -> None:
        os.makedirs("schedules", exist_ok=True)
        path = os.path.join("schedules", f"{self.name}.txt")
        with open(path, "w") as fh:
            for ts, pid in self._log:
                fh.write(f"({ts}, {pid})\n")
            fh.write(f"Average waiting time {self.average_waiting_time():.2f}\n")
        print(f"Output written to '{path}'")
