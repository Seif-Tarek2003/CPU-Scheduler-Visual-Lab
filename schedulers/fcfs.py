"""
First Come First Serve (FCFS) Scheduler
Non-preemptive. Processes are served in the order they arrive.
Ties in arrival time are broken by process ID (lexicographic).
"""

from __future__ import annotations
from typing import List

from simulator.process import Process
from simulator.base import BaseScheduler


class FCFS(BaseScheduler):
    name = "fcfs"

    def perform_schedule(self) -> None:
        # Sort by arrival time; break ties by pid
        queue: List[Process] = sorted(
            self.processes, key=lambda p: (p.arrival_time, p.pid)
        )

        clock = 0
        for process in queue:
            # CPU may be idle while waiting for the next process to arrive
            if clock < process.arrival_time:
                clock = process.arrival_time

            process.start_time = clock
            self.context_switch(clock, process.pid)

            clock += process.burst_time
            process.finish_time = clock
