"""
Shortest Job First (SJF) Scheduler — Non-Preemptive
When the CPU is free, pick the ready process with the smallest burst time.
Ties broken by arrival time, then pid.
"""

from __future__ import annotations
from typing import List

from simulator.process import Process
from simulator.base import BaseScheduler


class SJF(BaseScheduler):
    name = "sjf"

    def perform_schedule(self) -> None:
        pending: List[Process] = sorted(
            self.processes, key=lambda p: (p.arrival_time, p.pid)
        )
        done = 0
        clock = 0
        scheduled = [False] * len(pending)

        while done < len(pending):
            # Collect all processes that have arrived by `clock`
            ready = [
                p for p, s in zip(pending, scheduled)
                if not s and p.arrival_time <= clock
            ]

            if not ready:
                # CPU idle — jump to next arrival
                next_arrival = min(p.arrival_time for p, s in zip(pending, scheduled) if not s)
                clock = next_arrival
                continue

            # Pick shortest burst; break ties by arrival then pid
            process = min(ready, key=lambda p: (p.burst_time, p.arrival_time, p.pid))
            idx = pending.index(process)
            scheduled[idx] = True

            process.start_time = clock
            self.context_switch(clock, process.pid)

            clock += process.burst_time
            process.finish_time = clock
            done += 1
