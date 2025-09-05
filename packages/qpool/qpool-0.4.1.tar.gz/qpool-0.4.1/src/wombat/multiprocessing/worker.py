# File: src/wombat/multiprocessing/worker.py
"""
Worker process for wombat.
"""

from __future__ import annotations

import asyncio
import functools
import heapq
import importlib
import inspect
import logging
import os
import time
from collections import deque
from contextlib import AsyncExitStack
from enum import Enum
from queue import Full
from traceback import format_exc
from typing import TYPE_CHECKING, Any

import msgpack

from wombat.multiprocessing.models import (
    EOQ,
    ProgressUpdate,
    Prop,
    RequiresPropsTrait,
    ResultTaskPair,
    Task,
    TaskState,
    WorkerConfig,
)
from wombat.multiprocessing.progress import add
from wombat.multiprocessing.queues import log_task
from wombat.multiprocessing.utilities import (
    is_async_context_manager,
    is_sync_context_manager,
    queue_get_async,
)
from wombat.utils.dictionary import deep_merge

if TYPE_CHECKING:
    from collections.abc import Callable


class WorkerStatus(Enum):
    CREATED = 0
    RUNNING = 1
    SLEEPING = 2
    STOPPED = 3
    PAUSED = 4


class Worker:
    def __getstate__(self):
        state = self.__dict__.copy()
        # The process object is not picklable and should not be transferred
        # to the worker process. It's only managed by the Orchestrator.
        state["_process"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __init__(
        self,
        config: WorkerConfig,
        get_time: Callable[[], float] = time.monotonic,
    ) -> None:
        self.context = config.context
        self.total_progress_tasks = config.total_progress_tasks
        self.finished_tasks = (
            config.finished_tasks
            if config.finished_tasks is not None
            else self.context.Value("i", 0)
        )
        self.total_tasks = self.context.Value("i", 0)
        self.last_update = None
        self.get_time = get_time
        self.task_timestamps = deque()
        self.tasks_per_minute_limit = config.tasks_per_minute_limit
        self.start_time = get_time()
        self.id = config.worker_id
        self.name = config.name
        self.task_id = config.task_id
        self.control_queues = config.control_queues
        self.task_queue = config.task_queue
        self.log_queue = config.log_queue
        self.log(f"Worker __init__ in pid={os.getpid()}", logging.DEBUG)
        self.result_queue = config.result_queue
        self.retries = []  # heap of (ready_at, sequence, task)
        self.retry_counter = 0
        self.progress = ProgressUpdate(task_id=self.task_id)
        self.progress_delta = ProgressUpdate(task_id=self.task_id)
        self.progress_queue = config.progress_queue
        self.is_retrying = False
        self.filtered_props_cache = {}
        self.task_capabilities_cache = {}
        self.deduplication_cache: dict[str, float] = {}

        self.max_concurrent_tasks = config.max_concurrent_tasks
        self.semaphore: asyncio.Semaphore | None = None

        self.props = config.props
        self.status = config.status
        self.loop: asyncio.AbstractEventLoop | None = None
        self._retry_scheduled_event: asyncio.Event | None = None
        self._running_tasks: set[asyncio.Task] = set()

        try:
            self._process = self.context.Process(
                target=self.start_event_loop,
                kwargs={"packed_actions": config.packed_actions, "props": self.props},
                name=self.name,
            )
            if not self._process.is_alive():
                self.log(f"Worker {self.name} prepared for start", logging.DEBUG)
        except Exception:
            self.log(
                f"Worker {self.name} failed to initialize: \n{format_exc()}",
                logging.ERROR,
            )

    # ---------------------------
    # Debug / tracing utilities
    # ---------------------------

    def _trace_retry(self, task: Any, phase: str, extra: dict[str, Any] | None = None):
        """Emit a structured DEBUG line for retry diagnostics."""
        from wombat.multiprocessing.models import RetryableTrait

        try:
            tid = getattr(task, "id", "<no-id>")
            status = getattr(task, "status", "<na>")
            tries = extra.get("tries", "<na>") if extra else "<na>"
            if tries == "<na>" and hasattr(task, "traits"):
                retry_trait = next(
                    (t for t in task.traits if isinstance(t, RetryableTrait)), None
                )
                if retry_trait:
                    tries = retry_trait.tries
            payload = {
                "phase": phase,
                "task_id": str(tid),
                "tries": tries,
                "status": str(status),
            }
            if extra:
                payload.update(extra)
            self.log(f"RETRY_TRACE {payload}", logging.DEBUG)
        except Exception:
            # Never let tracing break execution.
            pass

    # ---------------------------
    # Progress & Logging helpers
    # ---------------------------

    def update_progress(self, *, force_update: bool = False):
        update = self.progress_delta.model_dump(exclude_unset=True)
        if self.progress_queue and (
            force_update
            or self.last_update is None
            or self.get_time() - self.last_update > 1
        ):
            self.last_update = self.get_time()
            merged = deep_merge(
                self.progress.model_dump(),
                update,
                strategies={
                    k: add if isinstance(v, (int, float)) else "override"
                    for k, v in self.progress.model_dump().items()
                },
            )
            self.progress = ProgressUpdate.parse_obj(merged)
            if self.total_progress_tasks:
                with self.total_progress_tasks.get_lock():
                    self.total_progress_tasks.value += 1
            self.progress_queue.put(
                Task(
                    action="progress",
                    requires_props=["process", "progress_bar", "progress"],
                    kwargs={"update": self.progress_delta},
                )
            )
            self.progress_delta = ProgressUpdate(task_id=self.task_id)

    def log(self, message: str, level: int):
        if self.log_queue:
            try:
                self.log_queue.put_nowait(
                    Task(
                        action="log",
                        traits=[
                            {
                                "trait_name": "requires_props",
                                "requires_props": ["logger"],
                            }
                        ],
                        kwargs={"message": message, "level": level},
                    )
                )
            except Full:
                # Log queue is full, drop message to prevent deadlock.
                pass

    # ---------------
    # Process control
    # ---------------

    def start(self):
        if not self._process.is_alive():
            self.log(
                f"Orchestrator is starting worker process in pid={os.getpid()}",
                logging.DEBUG,
            )
            self.log(f"Starting process for {self.name}", logging.DEBUG)
            self._process.start()
            with self.status.get_lock():
                self.status.value = WorkerStatus.RUNNING.value

    # -------------
    # Task execution
    # -------------

    async def execute_task(
        self, *, task: Task, func, props: dict[str, Prop], is_async: bool
    ):
        # 1. Before-execute hook
        task.status = TaskState.attempt
        allow_execution = True
        if hasattr(task, "traits"):
            for trait in task.traits:
                if not trait.on_before_execute(task, self):
                    allow_execution = False
                    break

        if not allow_execution:
            # Execution was cancelled by a hook (e.g., task expired).
            # The hook is responsible for setting the task's final status.
            self.progress_delta.failures += 1
            with self.finished_tasks.get_lock():
                self.finished_tasks.value += 1
            if self.result_queue:
                self.result_queue.put(
                    ResultTaskPair(
                        task=task, result="Task execution skipped by pre-flight hook."
                    )
                )
            self.update_progress()
            return

        last_exception = None
        result_data = None

        try:
            async def _execute() -> Any:
                # NOTE: With the change to a trait-based system, tasks are no longer
                #       loggable by default. This call will only log if the task
                #       instance has a `LoggableTrait` in its `traits` list.
                #       This behavior is intentional as part of the refactor.
                log_task(
                    queue=self.log_queue,
                    task=task,
                    message=f"Executing task: {task.id}",
                    level=logging.INFO,
                )

                args = task.args.copy() if hasattr(task, "args") else []
                kwargs = task.kwargs.copy() if hasattr(task, "kwargs") else {}

                requires_props_trait = next((t for t in task.traits if isinstance(t, RequiresPropsTrait)), None)
                if requires_props_trait:
                    kwargs["props"] = requires_props_trait.get_filtered_props(props)

                if is_async:
                    coroutine = func(self, *args, **kwargs)
                    return await coroutine
                else:
                    p = functools.partial(func, self, *args, **kwargs)
                    return await self.loop.run_in_executor(None, p)

            # Chain the around_execute hooks from all traits.
            # The innermost function is the actual execution.
            wrapped_execute = _execute
            if hasattr(task, "traits"):
                # Decorators stack, so we apply wrappers in reverse to match intuition.
                for trait in reversed(task.traits):
                    # functools.partial freezes the current value of wrapped_execute
                    # for the next iteration's wrapper.
                    wrapped_execute = functools.partial(trait.around_execute, task, self, wrapped_execute)

            # Call the fully wrapped execution chain.
            result_data = await wrapped_execute()

            # Let hooks decide if it's a success or failure based on the result.
            task.status = TaskState.success
            if hasattr(task, "traits"):
                for trait in task.traits:
                    trait.on_success(task, self, result_data)

        except asyncio.CancelledError:
            task.status = TaskState.cancel
            raise  # Re-raise to be handled by the caller.
        except Exception as e:  # noqa: BLE001, the worker must never die
            last_exception = format_exc()
            task.status = TaskState.fail
            if hasattr(task, "traits"):
                for trait in task.traits:
                    trait.on_failure(task, self, e)
            log_task(
                queue=self.log_queue,
                task=task,
                message=f"Error while executing task {task} with function {func}: {last_exception}",
                level=logging.ERROR,
            )
        finally:
            # The task's status is now the source of truth, set by the hooks.
            if task.status == TaskState.success:
                self.progress_delta.completed += 1
                with self.finished_tasks.get_lock():
                    self.finished_tasks.value += 1
                if self.result_queue:
                    self.result_queue.put(ResultTaskPair(task=task, result=result_data))

            elif task.status == TaskState.retry:
                # The retry has been scheduled by the trait's on_failure hook.
                self.progress_delta.retries += 1
            elif task.status == TaskState.cancel:
                # Cancellation is handled by _process_and_execute_task's except block.
                # Do not generate a result here to avoid duplicates.
                pass
            else:  # This covers .fail, .expired, and other terminal states
                self._trace_retry(task, "permanent_fail")
                self.progress_delta.failures += 1
                with self.finished_tasks.get_lock():
                    self.finished_tasks.value += 1
                if self.result_queue:
                    self.result_queue.put(
                        ResultTaskPair(task=task, result=[last_exception, result_data])
                    )
            self.update_progress()

    def _fail_task_on_shutdown(self, task: Task):
        """Marks a task as failed due to shutdown and records it."""
        if hasattr(task, "status"):
            task.status = TaskState.fail
        self.progress_delta.failures += 1
        if self.result_queue:
            self.result_queue.put(
                ResultTaskPair(
                    task=task,
                    result=["Task failed due to worker shutdown.", None],
                )
            )
        with self.finished_tasks.get_lock():
            self.finished_tasks.value += 1

    async def _process_and_execute_task(
        self, task: Task, from_task_queue: bool, actions: dict[str, Callable]
    ):
        """Helper coroutine to wrap the execution of a single task."""
        try:
            with self.status.get_lock():
                self.status.value = WorkerStatus.RUNNING.value
            await self.enforce_rate_limit()

            action_obj = actions.get(task.action)
            if action_obj:
                func = getattr(action_obj, "func", action_obj)
                is_async = inspect.iscoroutinefunction(func)
                await self.execute_task(
                    task=task, func=func, props=self.props, is_async=is_async
                )
            else:
                self.log(
                    f"No action '{task.action}' found for task {task.id}",
                    logging.ERROR,
                )
        except asyncio.CancelledError:
            self.log(f"Task {task.id} was cancelled during shutdown.", logging.INFO)
            self._fail_task_on_shutdown(task)
            raise  # Re-raise to signal cancellation
        except Exception as e:
            self.log(
                f"Unhandled exception processing task {task.id}: {e}", logging.ERROR
            )
            self._fail_task_on_shutdown(task)
        finally:
            if from_task_queue:
                self.task_queue.task_done()

    # ----------------------
    # Event loop & run logic
    # ----------------------

    def start_event_loop(self, packed_actions: bytes, props: dict[str, Any]):
        import uvloop  # noqa: PLC0415, want to retain the ability to support custom loops

        unpacked_actions = msgpack.unpackb(packed_actions, raw=False)
        actions = {}
        for k, v in unpacked_actions.items():
            if isinstance(v, str):
                try:
                    module_name, func_name = v.rsplit(".", 1)
                    module = importlib.import_module(module_name)
                    actions[k] = getattr(module, func_name)
                except (ValueError, ImportError, AttributeError):
                    actions[k] = v  # Not a function string, or can't import, leave as is
            else:
                actions[k] = v
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop = asyncio.new_event_loop()
        if self.max_concurrent_tasks is not None and self.max_concurrent_tasks > 0:
            self.semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
        self._retry_scheduled_event = asyncio.Event()
        asyncio.set_event_loop(self.loop)
        try:
            self.log(f"Entering start_event_loop in pid={os.getpid()}", logging.DEBUG)
            self.log(
                f"Starting event loop for {self.name}:{os.getpid()}",
                logging.CRITICAL,
            )
            self.loop.run_until_complete(self.run(actions=actions, props=props))
        finally:
            self.log(f"Event loop shutting down in pid={os.getpid()}", logging.DEBUG)
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()
            self.log(f"Event loop closed in pid={os.getpid()}", logging.DEBUG)

    async def enforce_rate_limit(self):
        if self.tasks_per_minute_limit is None:
            return

        with self.tasks_per_minute_limit.get_lock():
            # This is the tasks-per-minute limit for this specific worker.
            limit = self.tasks_per_minute_limit.value
        if limit <= 0:
            return

        now = self.get_time()

        # Prune timestamps that are older than 60 seconds from the rolling window.
        one_minute_ago = now - 60.0
        while self.task_timestamps and self.task_timestamps[0] < one_minute_ago:
            self.task_timestamps.popleft()

        # If the number of tasks in the last minute is at or above the limit,
        # we must wait until the oldest task is outside the 60-second window.
        if len(self.task_timestamps) >= limit:
            time_of_oldest_task = self.task_timestamps[0]
            wait_time = (time_of_oldest_task + 60.0) - now

            if wait_time > 0:
                self.log(
                    f"Worker {self.name} is rate-limited, sleeping for {wait_time:.2f} seconds",
                    logging.DEBUG,
                )
                await asyncio.sleep(wait_time)

        # Add the timestamp for the current task *after* waiting.
        self.task_timestamps.append(self.get_time())

    async def initialize_prop(
        self, *, props: dict[str, Prop], prop_name: str, reinitialize: bool = False
    ):
        try:
            prop = props[prop_name]
            initializer = prop.initializer
            resolved_value = prop.instance if not reinitialize else None
            exit_stack = prop.exit_stack if not reinitialize else AsyncExitStack()
            if exit_stack is None and prop.use_context_manager:
                exit_stack = AsyncExitStack()
            if resolved_value is None:
                if asyncio.iscoroutinefunction(initializer):
                    resolved_value = await initializer()
                elif callable(initializer):
                    # Run sync initializer in the event loop's default executor.
                    resolved_value = await self.loop.run_in_executor(None, initializer)
                else:
                    resolved_value = initializer
            if prop.use_context_manager and resolved_value:
                prop_is_async_cm = is_async_context_manager(resolved_value)
                prop_is_sync_cm = (
                    is_sync_context_manager(resolved_value)
                    if not prop_is_async_cm
                    else False
                )
                if prop_is_async_cm:
                    await exit_stack.enter_async_context(resolved_value)
                elif prop_is_sync_cm:
                    exit_stack.enter_context(resolved_value)
            # Modify the existing Prop object in-place to ensure the change is persistent
            # for the lifetime of the worker, instead of creating a new object.
            prop.instance = resolved_value
            prop.exit_stack = exit_stack
        except Exception as e:
            self.log(
                f"Worker {self.name} failed to initialize prop {prop_name}: {e}\n{format_exc()}",
                logging.ERROR,
            )
            return e

    async def _task_queue_producer(
        self, internal_queue: asyncio.Queue, initialization_complete: asyncio.Event
    ):
        """Monitors the main task queue and puts new tasks into the internal queue."""
        self.log("Task queue producer waiting for initialization.", logging.DEBUG)
        await initialization_complete.wait()
        self.log("Task queue producer started.", logging.DEBUG)

        while True:
            try:
                self.log("Task queue producer waiting on get().", logging.DEBUG)
                task = await queue_get_async(self.loop, self.task_queue)
                self.log(
                    f"Task queue producer got task: {getattr(task, 'id', 'N/A')}.",
                    logging.DEBUG,
                )
                if task:
                    with self.total_tasks.get_lock():
                        self.total_tasks.value += 1
                    await internal_queue.put((task, True))
            except (OSError, ValueError, asyncio.CancelledError, EOFError) as e:
                # An OSError or ValueError can occur if the queue is closed during shutdown.
                # A CancelledError can be raised when the worker is stopping.
                # EOFError is raised on POSIX when a closed queue is read from.
                self.log(
                    f"Task queue producer caught {type(e).__name__}, exiting.",
                    logging.DEBUG,
                )
                break

    async def _control_queue_producer(self, internal_queue: asyncio.Queue):
        """Monitors all control queues and puts messages into the internal queue."""
        self.log("Control queue producer started.", logging.DEBUG)
        control_queue = next(iter(self.control_queues.values()), None)
        if not control_queue:
            self.log("No control queue found, producer exiting.", logging.DEBUG)
            return

        while True:
            try:
                self.log("Control queue producer waiting on get().", logging.DEBUG)
                task = await queue_get_async(self.loop, control_queue)
                self.log(
                    f"Control queue producer got task: {getattr(task, 'action', 'N/A')}.",
                    logging.DEBUG,
                )
                if task:
                    control_queue.task_done()
                    await internal_queue.put((task, False))
                    # The exit task is the final message. Stop monitoring.
                    if task.action == "exit":
                        self.log(
                            "Control queue producer got exit signal, exiting.",
                            logging.DEBUG,
                        )
                        break
            except (OSError, ValueError, asyncio.CancelledError, EOFError) as e:
                self.log(
                    f"Control queue producer caught {type(e).__name__}, exiting.",
                    logging.DEBUG,
                )
                break

    async def _retry_producer(
        self, internal_queue: asyncio.Queue, initialization_complete: asyncio.Event
    ):
        """Monitors the retry heap and schedules retries via the internal queue."""
        self.log("Retry producer waiting for initialization.", logging.DEBUG)
        await initialization_complete.wait()
        self.log("Retry producer started.", logging.DEBUG)

        while True:
            try:
                if not self.retries:
                    # Heap is empty, wait for a new item to be scheduled.
                    self.log("Retry producer waiting for retry event.", logging.DEBUG)
                    await self._retry_scheduled_event.wait()
                    self._retry_scheduled_event.clear()
                    # A new item has arrived, loop to process it.
                    continue

                # Heap is not empty, check the soonest item.
                next_retry_time = self.retries[0][0]
                delay = next_retry_time - self.get_time()

                if delay > 0:
                    # The next retry is in the future. Wait for the delay to pass,
                    # or for a new retry to be scheduled, whichever comes first.
                    try:
                        await asyncio.wait_for(
                            self._retry_scheduled_event.wait(), timeout=delay
                        )
                        self._retry_scheduled_event.clear()
                        # New item arrived, loop to re-evaluate which is soonest.
                        continue
                    except asyncio.TimeoutError:
                        # The delay for the soonest item has passed.
                        # Fall through to process it.
                        pass

                # The soonest item is ready to be processed.
                ready_at, _, task = heapq.heappop(self.retries)
                self._trace_retry(task, "pop_retry_heap", {"ready_at": ready_at})
                await internal_queue.put((task, False))
            except asyncio.CancelledError:
                self.log("Retry producer cancelled, exiting.", logging.DEBUG)
                break

    async def run(self, *, actions: dict[str, Callable], props: dict[str, Prop]):
        self.log(f"Worker run method started in pid={os.getpid()}.", logging.DEBUG)
        self.props = props if props is not None else {}
        initialization_complete = asyncio.Event()

        async def initialize_all_props():
            """Initializes all props and sets an event upon completion."""
            self.log("Initializing all props.", logging.DEBUG)
            try:
                to_gather = [
                    self.initialize_prop(props=self.props, prop_name=prop_name)
                    for prop_name in self.props
                ]
                await asyncio.gather(*to_gather)
                self.log("Props initialized.", logging.DEBUG)
                self.log(f"Worker {self.name} initialization complete.", logging.INFO)
                initialization_complete.set()
            except asyncio.CancelledError:
                self.log(f"Worker {self.name} initialization cancelled.", logging.INFO)
            except Exception as e:
                self.log(
                    f"Worker {self.name} failed during prop initialization: {e}",
                    logging.CRITICAL,
                )

        init_task = self.loop.create_task(initialize_all_props())

        internal_queue = asyncio.Queue()
        task_queue_producer = self.loop.create_task(
            self._task_queue_producer(internal_queue, initialization_complete)
        )
        control_queue_producer = self.loop.create_task(
            self._control_queue_producer(internal_queue)
        )
        retry_producer = self.loop.create_task(
            self._retry_producer(internal_queue, initialization_complete)
        )
        producers = [task_queue_producer, control_queue_producer, retry_producer]

        async def semaphore_wrapper(task, from_task_queue, actions):
            if self.semaphore:
                async with self.semaphore:
                    await self._process_and_execute_task(task, from_task_queue, actions)
            else:
                await self._process_and_execute_task(task, from_task_queue, actions)

        try:
            self.log("Main worker loop starting.", logging.DEBUG)
            self.log(f"Worker {self.name} is running", logging.INFO)
            with self.status.get_lock():
                self.status.value = WorkerStatus.RUNNING.value
            self.progress_delta.status = f"Starting {self.name}"

            while True:
                with self.status.get_lock():
                    self.status.value = WorkerStatus.SLEEPING.value

                self.log("Main loop waiting for internal queue.", logging.DEBUG)
                task, from_task_queue = await internal_queue.get()
                self.log(
                    f"Main loop got task from internal queue: {getattr(task, 'action', 'N/A')}.",
                    logging.DEBUG,
                )

                if task.action == "exit":
                    self.log("Main loop received exit signal.", logging.DEBUG)
                    if not init_task.done():
                        init_task.cancel()
                    if self._running_tasks:
                        self.log(
                            f"Cancelling {len(self._running_tasks)} running tasks.",
                            logging.INFO,
                        )
                        for t in self._running_tasks:
                            t.cancel()

                    retry_producer.cancel()
                    task_queue_producer.cancel()

                    tasks_to_fail = len(self.retries)
                    while not internal_queue.empty():
                        queued_task, _ = internal_queue.get_nowait()
                        if queued_task.action != "exit":
                            self._fail_task_on_shutdown(queued_task)
                            tasks_to_fail += 1

                    self.log(
                        f"Received exit task in worker {self.name}. Failing {tasks_to_fail} pending tasks.",
                        logging.INFO,
                    )
                    for _, _, retry_task in self.retries:
                        self._fail_task_on_shutdown(retry_task)
                    self.retries.clear()
                    self.update_progress(force_update=True)
                    self.log(
                        f"Worker {self.name} finished failing pending tasks. Exiting.",
                        logging.INFO,
                    )
                    self.log("Exiting main run loop.", logging.DEBUG)
                    return

                if isinstance(task, Task):
                    bg_task = self.loop.create_task(
                        semaphore_wrapper(task, from_task_queue, actions)
                    )
                    self._running_tasks.add(bg_task)
                    bg_task.add_done_callback(self._running_tasks.discard)
        except Exception as e:
            self.log(
                f"Worker {self.name} encountered a fatal exception: {e}\n{format_exc()}",
                logging.ERROR,
            )
        finally:
            self.log("Main run loop finally block.", logging.DEBUG)
            # Do not cancel producers; they must exit gracefully. Cancellation
            # can leave executor threads in a stuck state on a blocking queue.get().
            await asyncio.gather(*producers, init_task, return_exceptions=True)
            with self.status.get_lock():
                self.status.value = WorkerStatus.STOPPED.value
            if self.progress_queue:
                self.progress_delta.status = f"Stopping worker {self.name}"
                self.update_progress(force_update=True)
            for prop in self.props.values():
                if prop.use_context_manager and prop.exit_stack:
                    await prop.exit_stack.aclose()
            if self.result_queue:
                self.log("Putting EOQ on result queue.", logging.DEBUG)
                self.result_queue.put(ResultTaskPair(task=EOQ(), result=None))
            self.log("Worker run finished.", logging.DEBUG)
