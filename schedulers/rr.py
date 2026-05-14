"""
Round Robin (RR) Scheduler
Preemptive. Each process gets a fixed time slice (quantum) before
being preempted and placed at the back of the ready queue.
"""

from __future__ import annotations
from collections import deque
from typing import List

from simulator.process import Process
from simulator.base import BaseScheduler


class RR(BaseScheduler):
    name = "rr"

    def __init__(self, processes: List[Process], quantum: int = 2):
        super().__init__(processes)
        self.quantum = quantum

    def perform_schedule(self) -> None:
        # Sort by arrival time so we can add them to the queue on time
        pending: List[Process] = sorted(
            self.processes, key=lambda p: (p.arrival_time, p.pid)
        )

        ready: deque[Process] = deque()
        clock = 0
        pending_idx = 0
        current_pid: str | None = None  # track last running process for context-switch detection

        # Seed any processes that arrive at time 0
        while pending_idx < len(pending) and pending[pending_idx].arrival_time <= clock:
            ready.append(pending[pending_idx])
            pending_idx += 1

        while ready or pending_idx < len(pending):
            if not ready:
                # CPU idle — fast-forward to next arrival
                clock = pending[pending_idx].arrival_time
                while pending_idx < len(pending) and pending[pending_idx].arrival_time <= clock:
                    ready.append(pending[pending_idx])
                    pending_idx += 1

            process = ready.popleft()

            if process.start_time == -1:
                process.start_time = clock

            # Log context switch only when the running process changes
            if process.pid != current_pid:
                self.context_switch(clock, process.pid)
                current_pid = process.pid

            # Run for min(quantum, remaining burst)
            run_time = min(self.quantum, process.remaining)
            process.remaining -= run_time
            clock += run_time

            # Enqueue newly arrived processes during this slice
            while pending_idx < len(pending) and pending[pending_idx].arrival_time <= clock:
                ready.append(pending[pending_idx])
                pending_idx += 1

            if process.remaining > 0:
                ready.append(process)    # preempt — re-queue
                current_pid = None       # force log on next pick
            else:
                process.finish_time = clock
