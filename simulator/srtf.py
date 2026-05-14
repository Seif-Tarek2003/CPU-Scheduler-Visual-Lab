"""
Shortest Remaining Time First (SRTF) Scheduler — Preemptive SJF
At every new arrival (or completion), re-pick the process with the
least remaining burst time. The current process is preempted if a
shorter job arrives.
"""

from __future__ import annotations
from typing import List, Optional

from simulator.process import Process
from simulator.base import BaseScheduler


class SRTF(BaseScheduler):
    name = "srtf"

    def perform_schedule(self) -> None:
        # Work on copies already provided by BaseScheduler
        pending: List[Process] = sorted(
            self.processes, key=lambda p: p.arrival_time
        )

        # Collect all distinct event timestamps (arrivals + completion moments)
        # We simulate tick-by-tick but skip idle gaps using event-driven logic.
        total_burst = sum(p.burst_time for p in pending)
        clock = 0
        done = 0
        current: Optional[Process] = None
        last_switch_time = 0

        # We'll advance one unit at a time when processes are running —
        # but skip ahead over idle CPU gaps.
        arrived: List[Process] = []
        pending_iter = iter(sorted(pending, key=lambda p: p.arrival_time))
        arrival_queue = list(pending)  # sorted copy for iteration
        arrival_queue.sort(key=lambda p: p.arrival_time)
        arrival_idx = 0

        while done < len(pending):
            # Admit all processes that have arrived by clock
            while arrival_idx < len(arrival_queue) and arrival_queue[arrival_idx].arrival_time <= clock:
                arrived.append(arrival_queue[arrival_idx])
                arrival_idx += 1

            if not arrived:
                # CPU idle: jump to next arrival
                clock = arrival_queue[arrival_idx].arrival_time
                continue

            # Pick process with minimum remaining time; tie-break by arrival, pid
            best: Process = min(arrived, key=lambda p: (p.remaining, p.arrival_time, p.pid))

            # Detect context switch
            if best is not current:
                self.context_switch(clock, best.pid)
                if best.start_time == -1:
                    best.start_time = clock
                current = best

            # Determine how long this process runs before an event:
            # either the next arrival or its own completion — whichever is sooner.
            next_arrival = (
                arrival_queue[arrival_idx].arrival_time
                if arrival_idx < len(arrival_queue)
                else float("inf")
            )
            run_until = min(clock + best.remaining, next_arrival)
            elapsed = int(run_until) - clock

            best.remaining -= elapsed
            clock += elapsed

            # Admit processes that just arrived at this new clock
            while arrival_idx < len(arrival_queue) and arrival_queue[arrival_idx].arrival_time <= clock:
                arrived.append(arrival_queue[arrival_idx])
                arrival_idx += 1

            if best.remaining == 0:
                best.finish_time = clock
                arrived.remove(best)
                done += 1
                current = None  # force re-evaluation next iteration
