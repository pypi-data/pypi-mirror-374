# File: src/wombat/multiprocessing/orchestrator.py
# region Imports [ rgba(0,0,0,0.5) ]
from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Callable, Generator
from functools import partial
from multiprocessing import get_context
from threading import Event, Lock, Thread
from typing import (
    Annotated,
    Any,
)
from uuid import uuid4

import msgpack
from annotated_types import Ge

from wombat.multiprocessing.errors import UnpicklablePayloadError, WorkerCrashError
from wombat.multiprocessing.log import log, setup_logging
from wombat.multiprocessing.models import (
    ProgressUpdate,
    ResultTaskPair,
    Task,
    TaskState,
    UninitializedProp,
    WorkerConfig,
)
from wombat.multiprocessing.progress import run_progress
from wombat.multiprocessing.queues import (
    ControlQueue,
    LogQueue,
    ProgressQueue,
    ResultQueue,
    TaskQueue,
    default_encoder,
    drain_queue_non_blocking,
)
from wombat.multiprocessing.worker import Worker, WorkerStatus
from wombat.utils.errors.decorators import enforce_type_hints_contracts

# endregion


class Orchestrator:
    @enforce_type_hints_contracts
    def __init__(
        self,
        num_workers: Annotated[int, Ge(0)],
        actions: dict[str, Callable] | None = None,
        props: dict[str, Any] | None = None,
        show_progress: bool = False,
        task_models: list[type[Task]] | None = None,
        tasks_per_minute_limit: int | None = None,
        logging_config: dict[str, Any] | None = None,
        max_concurrent_tasks: int | None = None,
    ):
        task_models = (
            task_models if task_models is not None and len(task_models) > 0 else [Task]
        )
        self.context = get_context("spawn")
        self.tasks_per_minute_limit = (
            self.context.Value("d", tasks_per_minute_limit / num_workers)
            if tasks_per_minute_limit and num_workers > 0
            else None
        )

        self._results_buffer: list[ResultTaskPair] = []
        self.total_progress_tasks = self.context.Value("i", 0)
        self.finished_tasks = self.context.Value("i", 0)
        self.results_collected_count = self.context.Value("i", 0)
        self.total_tasks = 0
        self.total_tasks_lock = Lock()
        self._results_buffer_lock = Lock()
        self._stop_event = Event()
        self._result_collection_task: asyncio.Task | None = None
        self.loop: asyncio.AbstractEventLoop | None = None
        self._completion_queue: asyncio.Queue | None = None
        self.props = props if props is not None else {}
        self.started = False
        self.stopped = False
        self.task_queue = TaskQueue(
            context=self.context, name="tasks", models=task_models, joinable=True
        )
        self.log_queue = LogQueue(context=self.context, name="log", joinable=True)
        self.result_queue = ResultQueue(context=self.context, name="results")
        logger_id = uuid4()
        control_queue_name = f"control-{logger_id}"
        self.logger_control_queues = {
            f"{control_queue_name}": ControlQueue(
                context=self.context,
                name=f"{control_queue_name}",
                joinable=True,
            )
        }
        self.worker_control_queues = {}
        self.workers = []
        self.show_progress = show_progress
        self.progress_thread = None
        self.progress_queue = None
        if show_progress:
            self.progress_queue = ProgressQueue(
                context=self.context, name="progress", joinable=True
            )
            self.total_progress_tasks = self.context.Value("i", 0)

        self.worker_states = {
            f"logger-{logger_id}": self.context.Value("i", WorkerStatus.CREATED.value)
        }
        logging_config = logging_config or {}

        actions = actions if actions is not None else {}
        packed_actions = msgpack.packb(actions, default=default_encoder, use_bin_type=True)

        packed_logger_actions = msgpack.packb(
            {"log": log}, default=default_encoder, use_bin_type=True
        )
        logger_config = WorkerConfig(
            context=self.context,
            name=f"logger-{logger_id}",
            worker_id=uuid4(),
            task_id=-1,
            packed_actions=packed_logger_actions,
            props={
                "logger": UninitializedProp(
                    initializer=partial(setup_logging, **logging_config),
                    use_context_manager=False,
                )
            },
            control_queues={"primary": self.logger_control_queues[control_queue_name]},
            task_queue=self.log_queue,
            result_queue=None,
            log_queue=None,
            progress_queue=None,
            status=self.worker_states[f"logger-{logger_id}"],
            finished_tasks=self.context.Value("i", 0),
            total_progress_tasks=None,
            tasks_per_minute_limit=None,
            max_concurrent_tasks=None,
        )
        self.logger = Worker(config=logger_config)
        self.log(f"Orchestrator initialized in pid={os.getpid()}", logging.DEBUG)
        for i in range(num_workers):
            worker_id = uuid4()
            worker_name = f"worker-{i}"
            control_queue_name = f"control-{worker_id}"
            self.worker_states[worker_name] = self.context.Value(
                "i", WorkerStatus.CREATED.value
            )
            self.worker_control_queues[control_queue_name] = ControlQueue(
                context=self.context, name=control_queue_name, joinable=True
            )
            worker_config = WorkerConfig(
                context=self.context,
                name=worker_name,
                worker_id=worker_id,
                task_id=i,
                packed_actions=packed_actions,
                props=self.props,
                control_queues={
                    "primary": self.worker_control_queues[control_queue_name]
                },
                task_queue=self.task_queue,
                result_queue=self.result_queue,
                log_queue=self.log_queue,
                progress_queue=self.progress_queue,
                status=self.worker_states[worker_name],
                finished_tasks=self.finished_tasks,
                total_progress_tasks=self.total_progress_tasks,
                tasks_per_minute_limit=self.tasks_per_minute_limit,
                max_concurrent_tasks=max_concurrent_tasks,
            )
            self.workers.append(Worker(config=worker_config))

    async def __aenter__(self):
        """Starts workers and returns the orchestrator instance."""
        self.log(f"Entering __aenter__ in pid={os.getpid()}", logging.DEBUG)
        await self.start_workers()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensures workers are stopped on context exit."""
        self.log(f"Entering __aexit__ in pid={os.getpid()}", logging.DEBUG)
        if self.started and not self.stopped:
            self.log(
                f"Orchestrator shutting down from context exit ({exc_type.__name__ if exc_type else 'normal exit'}).",
                logging.INFO,
            )
            await self.stop_workers(timeout=10.0)

    async def _collect_results_continuously_async(
        self, num_workers_to_expect: int, completion_queue: asyncio.Queue
    ):
        """Continuously drains the result queue in a dedicated asyncio task."""
        from wombat.multiprocessing.utilities import queue_get_async

        self.log("Result collector task running.", logging.DEBUG)
        eoq_received = 0
        while eoq_received < num_workers_to_expect and not self._stop_event.is_set():
            try:
                result = await queue_get_async(self.loop, self.result_queue)
                # ResultQueue is non-joinable, so no task_done() is needed.
                if hasattr(result.task, "sentinel") and result.task.sentinel == "EOQ":
                    eoq_received += 1
                    self.log(
                        f"Received EOQ ({eoq_received}/{num_workers_to_expect}).",
                        logging.DEBUG,
                    )
                else:
                    self.log(
                        f"Collected result for task {getattr(result.task, 'id', 'N/A')}.",
                        logging.DEBUG,
                    )
                    with self._results_buffer_lock:
                        self._results_buffer.append(result)
                    with self.results_collected_count.get_lock():
                        self.results_collected_count.value += 1
                    await completion_queue.put(None)
            except (EOFError, asyncio.CancelledError):
                self.log(
                    "Result collector task cancelled or queue closed.", logging.INFO
                )
                break
            except Exception as e:
                self.log(f"Result collector encountered an error: {e}", logging.ERROR)
                break

        self.log("Result collector task loop finished.", logging.DEBUG)
        # After the loop, perform a final drain to catch any stragglers.
        remaining_results = drain_queue_non_blocking(self.result_queue)
        with self._results_buffer_lock:
            for result in remaining_results:
                if not (
                    hasattr(result.task, "sentinel") and result.task.sentinel == "EOQ"
                ):
                    self._results_buffer.append(result)
        self.log("Result collector task exiting.", logging.DEBUG)

    @enforce_type_hints_contracts
    def update_progress(self, update: ProgressUpdate):
        with self.total_progress_tasks.get_lock():
            self.total_progress_tasks.value += 1
        if self.show_progress and self.progress_queue:
            self.progress_queue.put(
                Task(
                    action="progress",
                    requires_props=["process", "progress_bar", "progress"],
                    kwargs={
                        "update": update,
                    },
                )
            )

    @enforce_type_hints_contracts
    def log(self, message: str, level: int):
        self.log_queue.put(
            Task(
                action="log",
                traits=[{"trait_name": "requires_props", "requires_props": ["logger"]}],
                kwargs={
                    "message": message,
                    "level": level,
                },
            )
        )

    async def start_workers(self):
        """Starts workers and optionally monitors progress."""
        self.log("Entering start_workers...", logging.DEBUG)
        if self.started:
            self.log("Already started, returning.", logging.DEBUG)
            return
        self.started = True

        self.loop = asyncio.get_running_loop()
        self._completion_queue = asyncio.Queue()

        self.logger.start()
        self.log("Logger process starting.", logging.DEBUG)
        # Start workers
        self.log(
            message=f"Started logger with id {self.logger.id} and name {self.logger.name}",
            level=logging.DEBUG,
        )

        for worker in self.workers:
            worker.start()
        self.log("All worker processes starting.", logging.DEBUG)

        self._result_collection_task = self.loop.create_task(
            self._collect_results_continuously_async(
                num_workers_to_expect=len(self.workers),
                completion_queue=self._completion_queue,
            )
        )
        self.log("Result collector task started.", logging.DEBUG)

        if self.show_progress:
            self.progress_thread = Thread(
                target=run_progress,
                args=(
                    self.progress_queue,
                    len(self.workers),
                    self.total_progress_tasks,
                ),
                daemon=True,
            )
            self.progress_thread.start()

    async def finish_tasks(self, timeout: float | None = None):
        """
        Asynchronously waits for all tasks submitted *at the time of calling* to complete.

        This method is non-blocking and waits for completion signals from the
        result collector thread.

        Args:
            timeout (Optional[float]): If specified, the maximum time in seconds to
                wait. If the timeout is reached, a warning is logged.
        """
        self.log("Entering finish_tasks...", logging.DEBUG)
        with self.total_tasks_lock:
            tasks_to_finish = self.total_tasks

        with self.results_collected_count.get_lock():
            tasks_already_collected = self.results_collected_count.value

        tasks_remaining = tasks_to_finish - tasks_already_collected

        if not self.workers or tasks_remaining <= 0:
            self.log(
                message=f"No pending tasks to finish (Total: {tasks_to_finish}, Collected: {tasks_already_collected}).",
                level=logging.INFO,
            )
            return

        self.log(
            message=f"Finishing work: waiting for {tasks_remaining} tasks to complete.",
            level=logging.INFO,
        )
        self.update_progress(ProgressUpdate(task_id=-1, status="Finishing work"))

        try:
            async with asyncio.timeout(timeout):
                for _ in range(tasks_remaining):
                    # Liveness check to prevent hangs from crashed workers.
                    for worker in self.workers:
                        if not worker._process.is_alive():
                            error_msg = f"Worker {worker.name} crashed unexpectedly. Aborting wait."
                            self.log(error_msg, logging.CRITICAL)
                            raise WorkerCrashError(error_msg)
                    await self._completion_queue.get()
                    self._completion_queue.task_done()
        except TimeoutError:
            self.log(
                f"finish_tasks timed out after {timeout} seconds waiting for tasks to complete.",
                logging.WARNING,
            )

    def _get_buffered_results(self) -> list[ResultTaskPair]:
        """Returns and clears the internal results buffer in a thread-safe manner."""
        with self._results_buffer_lock:
            results = self._results_buffer
            self._results_buffer = []
            return results

    def get_results(self) -> Generator[ResultTaskPair]:
        """
        Yields all results collected from workers that are currently in the buffer.
        This method is non-blocking and provides a snapshot of completed tasks.
        """
        self.log(message="Getting results from buffer", level=logging.INFO)
        self.update_progress(ProgressUpdate(task_id=-1, status="Getting results"))

        # Yield all results currently held in the thread-safe buffer.
        # The background result collector thread is the only component that
        # interacts with the multiprocessing result queue.
        buffered = self._get_buffered_results()
        for item in buffered:
            yield item

    async def stop_workers(self, timeout: float | None = None) -> list[ResultTaskPair]:
        """Gracefully stops all workers, waits for tasks to finish, and collects results."""
        self.log("Entering stop_workers...", logging.DEBUG)
        if not self.started:
            self.log(
                message="Orchestrator not started. No workers to stop.",
                level=logging.INFO,
            )
            return []

        if self.stopped:
            self.log(
                message="Orchestrator already stopped. Ignoring call.",
                level=logging.WARNING,
            )
            return []
        self.stopped = True

        self.log(
            message="Stopping workers and finishing all tasks.", level=logging.INFO
        )
        # Asynchronously wait for all tasks to finish.
        await self.finish_tasks(timeout=timeout)
        self.log("finish_tasks completed.", logging.DEBUG)

        # 1. Signal workers to exit gracefully.
        self.log("Closing task queue.", logging.DEBUG)
        self.task_queue.close()
        # Ensure the queue's feeder thread is joined, which helps signal EOF to readers.
        await self.loop.run_in_executor(None, self.task_queue.queue.join_thread)
        self.log("Signaling workers to exit.", logging.INFO)
        for control_queue in self.worker_control_queues.values():
            control_queue.put(Task(action="exit"))
        self.log("Sent exit signal to all workers.", logging.DEBUG)

        # 2. Wait for worker processes to terminate. This is safer than joining queues,
        # as it won't hang if a worker has already crashed.
        self.update_progress(ProgressUpdate(task_id=-1, status="Joining processes"))
        self.log("Joining worker processes", logging.INFO)

        async def join_process(worker):
            # Attempt to join the worker process with a timeout.
            await self.loop.run_in_executor(None, worker._process.join, 5.0)
            if worker._process.is_alive():
                self.log(
                    f"Worker {worker.name} did not exit gracefully after 5.0 seconds. "
                    "Task cancellation is expected to handle shutdown without force.",
                    logging.WARNING,
                )
            else:
                self.log(f"Worker {worker.name} has exited.", level=logging.DEBUG)

        self.log("Waiting to join worker processes...", logging.DEBUG)
        await asyncio.gather(*(join_process(w) for w in self.workers))
        self.log("Worker processes joined.", logging.DEBUG)
        self.log(message="All workers have exited", level=logging.INFO)

        # Now that processes are stopped, we can safely close the control queues.
        for control_queue in self.worker_control_queues.values():
            control_queue.close()
        self.log("Worker control queues closed.", logging.DEBUG)

        # 3. Now that workers are terminated, clean up queues without joining.
        # Joining a queue after its consumer process may have been killed can
        # lead to a permanent deadlock if the killed process did not call
        # task_done() for an item it retrieved.
        self.update_progress(ProgressUpdate(task_id=-1, status="Closing queues"))
        self.log("Cleaning up worker queues.", logging.DEBUG)

        self._stop_event.set()
        self.log("Stop event set for result collector task.", logging.DEBUG)
        if self._result_collection_task:
            try:
                await asyncio.wait_for(self._result_collection_task, timeout=5.0)
                self.log("Result collector task finished.", logging.DEBUG)
            except asyncio.TimeoutError:
                self.log(
                    "Result collector task timed out, cancelling.", logging.WARNING
                )
                self._result_collection_task.cancel()

        results: list[ResultTaskPair] = self._get_buffered_results()

        self.update_progress(
            ProgressUpdate(task_id=-1, status="Closing final resources")
        )
        if self.show_progress and self.progress_queue and self.progress_thread:
            self.update_progress(ProgressUpdate(task_id=-1, total=-1))
            self.progress_queue.close()
            await self.loop.run_in_executor(None, self.progress_thread.join)

        # Wait for all log messages to be processed before signaling the logger to exit.
        self.log("Waiting for log queue to be processed.", logging.DEBUG)
        await self.loop.run_in_executor(None, self.log_queue.join)
        self.log_queue.close()
        # Ensure the queue's feeder thread is joined to signal EOF to the logger.
        await self.loop.run_in_executor(None, self.log_queue.queue.join_thread)

        # Signal the logger to exit, then close queues without joining.
        self.log("Signaling logger to exit.", logging.DEBUG)
        for queue in self.logger_control_queues.values():
            queue.put(Task(action="exit"))
            # The logger also uses a joinable queue, so we wait for acknowledgment.
            await self.loop.run_in_executor(None, queue.join)
            queue.close()
        self.log("Logger control queue joined and closed.", logging.DEBUG)

        self.log("Waiting to join logger process...", logging.DEBUG)
        await self.loop.run_in_executor(None, self.logger._process.join, 5.0)
        self.log("Logger process joined. Exiting stop_workers.", logging.DEBUG)
        return results

    @enforce_type_hints_contracts
    async def add_task(self, task: Task):
        """Adds a single task to the queue. Convenience wrapper around add_tasks."""
        await self.add_tasks([task])

    @enforce_type_hints_contracts
    async def add_tasks(self, tasks: list[Task]) -> list[Task]:
        """Adds a batch of tasks to the queue and starts workers if not already running."""
        self.log(f"Entering add_tasks for {len(tasks)} tasks...", logging.DEBUG)
        if not self.started:
            await self.start_workers()

        successfully_added = 0
        enqueue_failures = []
        for task in tasks:
            if hasattr(task, "status"):
                task.status = TaskState.queue
            try:
                if self.task_queue.put(task):
                    successfully_added += 1
                else:
                    # Validator failed in the queue's put method
                    enqueue_failures.append(task)
            except UnpicklablePayloadError as e:
                # Construct the error message carefully to ensure it's picklable.
                error_message = (
                    f"Failed to enqueue task {getattr(task, 'id', 'N/A')}. "
                    f"The task or its payload is not picklable. Original error: {e!s}"
                )
                self.log(error_message, logging.ERROR)
                enqueue_failures.append(task)

        with self.total_tasks_lock:
            self.total_tasks += successfully_added

        # Update progress if progress monitoring is enabled
        if self.show_progress and self.progress_queue and successfully_added > 0:
            self.update_progress(
                ProgressUpdate(
                    task_id=-1,
                    total=successfully_added,
                )
            )
        self.log(
            message=f"Added {successfully_added} tasks to the task queue. Failures: {len(enqueue_failures)}",
            level=logging.DEBUG,
        )
        return enqueue_failures
