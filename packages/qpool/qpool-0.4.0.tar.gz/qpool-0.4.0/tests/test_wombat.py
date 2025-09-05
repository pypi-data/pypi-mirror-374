from __future__ import annotations

import asyncio
import logging
import os
import ssl
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch
from uuid import uuid4

import aiohttp
import certifi
import pytest
import pytest_check as check
import requests
from aiohttp import ClientError, ClientSession

import tests.helpers
from tests.helpers import (
    evaluate_conditionally,
    fail_action,
    fail_conditionally,
)
from wombat.multiprocessing import (
    evaluatable,
    expirable,
    requires_props,
    retryable,
    task,
)
from wombat.multiprocessing.models import Prop, Task, TaskState
from wombat.multiprocessing.orchestrator import Orchestrator

if TYPE_CHECKING:
    from wombat.multiprocessing.worker import Worker

from multiprocessing import get_context

from wombat.multiprocessing.models import ResultTaskPair
from wombat.multiprocessing.queues import ResultQueue, drain_queue_non_blocking


def test_drain_non_joinable_queue():
    """
    Ensures drain_queue_non_blocking works correctly with non-joinable queues.

    It should not raise an error because task_done() is not supported on a
    standard multiprocessing.Queue.
    """
    context = get_context("spawn")
    # A ResultQueue is non-joinable by default.
    queue = ResultQueue(context=context, name="test_results")

    task = Task(action="test")
    item = ResultTaskPair(task=task, result="success")

    # Add items to the queue
    for _ in range(5):
        queue.put(item)

    # Allow the queue's feeder thread time to move items into the queue.
    time.sleep(0.1)

    # Drain the queue. This should not raise an error.
    results = drain_queue_non_blocking(queue)

    assert len(results) == 5
    assert all(isinstance(r, ResultTaskPair) for r in results)

    # The queue should now be empty.
    assert queue.empty()


def init_aiohttp_session() -> ClientSession:
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))


@task()
@requires_props(requires_props=["aiohttp_session"])
async def async_fetch_url(worker: Worker, url: str, props: dict[str, Prop]):
    session_prop: Prop = props["aiohttp_session"]
    session: ClientSession = session_prop.instance
    try:
        if not session:
            error = "aiohttp session prop is not initialized"
            raise RuntimeError(error)
        async with session.get(url) as resp:
            resp.raise_for_status()
            return resp.status
    except ClientError as e:
        worker.log(f"Connection error: {e}. Re-initializing session.", logging.WARNING)
        if session_prop and session_prop.exit_stack:
            await session_prop.exit_stack.aclose()
        await worker.initialize_prop(
            props=worker.props, prop_name="aiohttp_session", reinitialize=True
        )
        raise


@task()
async def hang_forever(_worker: Worker):
    """An action that deliberately hangs."""
    while True:
        await asyncio.sleep(1)


async def hang_initializer():
    """An async initializer that hangs forever."""
    while True:
        await asyncio.sleep(1)


@task()
def sleep_then_finish(_worker: Worker, duration: float):
    """An action that sleeps for a given duration."""
    time.sleep(duration)


def failing_initializer():
    """An initializer that is guaranteed to fail."""
    error = "Prop initialization failed"
    raise ValueError(error)


@task()
@requires_props(requires_props=["failing_prop"])
def use_prop(_worker: Worker, props: dict[str, Prop]):
    """An action that attempts to use a prop."""
    if not props["failing_prop"].instance:
        error = "Prop was not initialized"
        raise ValueError(error)


@task()
@requires_props(requires_props=["aiohttp_session"])
async def mock_async_fetch_url_success(
    worker: Worker, url: str, props: dict[str, Prop]
):
    """A mock action that simulates a successful async URL fetch."""
    await asyncio.sleep(0.01)
    return 200


@task()
def noop(worker: Worker):
    """An action that does nothing, quickly."""


@task()
def log_a_message(worker: Worker, message: str, level: int):
    """An action that logs a specific message."""
    worker.log(message, level)


def is_ok_evaluator(result: str) -> bool:
    """An evaluator function that checks if the result is 'OK'."""
    return result == "OK"


@task()
@expirable(expires_after=timedelta(seconds=-1))
def expired_action(_worker: Worker):
    """This action should never run, used to test on_before_execute."""
    # Use a file or other side effect to check for execution
    with open("test_on_before_execute.tmp", "w") as f:
        f.write("executed")


@task()
@evaluatable()
def dummy_action_for_unpicklable():
    pass


@task()
@retryable()
def backoff_action():
    pass


@pytest.fixture(scope="function")
def manager():
    """Function-scoped multiprocessing manager to ensure lifecycle."""
    context = get_context("spawn")
    with context.Manager() as m:
        yield m


orchestrator_configs = {
    "async": {
        "props": {
            "aiohttp_session": Prop(initializer=init_aiohttp_session),
        },
    },
    "fail": {
        "props": {},
    },
    "hang": {"props": {}},
    "sleep": {"props": {}},
    "failing_prop": {
        "props": {"failing_prop": Prop(initializer=failing_initializer)},
    },
    "noop": {"props": {}},
    "conditional_fail": {
        "props": {},  # props will be added dynamically in test
    },
    "logging_test": {
        "props": {},
    },
    "evaluatable_test": {
        "props": {},  # props will be added dynamically in test
    },
}


@pytest.fixture
def conditional_fail_config(manager):
    """Provides orchestrator config with shared props for conditional failure tests."""
    attempt_tracker = manager.dict()
    lock = manager.Lock()
    config = {
        "props": {
            "attempt_tracker": Prop(
                initializer=attempt_tracker, use_context_manager=False
            ),
            "lock": Prop(initializer=lock, use_context_manager=False),
        }
    }
    return config, attempt_tracker


@pytest.mark.asyncio
async def test_orchestrator_async(logging_config):
    sizes = [100, 200, 300, 400, 500]
    test_urls = [f"https://picsum.photos/{size}" for size in sizes]
    tasks = [mock_async_fetch_url_success(url) for url in test_urls]

    config = orchestrator_configs["async"].copy()
    test_actions = {
        mock_async_fetch_url_success.action_name: mock_async_fetch_url_success
    }

    async with Orchestrator(
        num_workers=4,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
        **config,
    ) as orchestrator:
        await orchestrator.add_tasks(tasks)
        job_results = await orchestrator.stop_workers()

    check.equal(len(job_results), len(sizes), "Expected correct number of results")
    errors = sum(1 for r in job_results if not isinstance(r.result, int))
    check.equal(errors, 0, "Expected no errors in async approach")
    check.is_true(
        all(r.result == requests.codes.ok for r in job_results), "Expected all 200s"
    )


@pytest.mark.asyncio
async def test_orchestrator_init_with_zero_workers(logging_config):
    """Verify Orchestrator can be initialized with zero workers without error."""
    try:
        async with Orchestrator(
            num_workers=0,
            show_progress=False,
            tasks_per_minute_limit=120,
            logging_config=logging_config,
        ) as orchestrator:
            check.equal(len(orchestrator.workers), 0)
            results = await orchestrator.stop_workers()
            check.equal(len(results), 0)
    except ZeroDivisionError:
        pytest.fail(
            "Orchestrator raised ZeroDivisionError with num_workers=0 and tasks_per_minute_limit"
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("show_progress", [True, False])
async def test_repeatedly_finish_tasks(logging_config, show_progress):
    tasks = [fail_action() for _ in range(10)]
    test_actions = {fail_action.action_name: fail_action}
    async with Orchestrator(
        num_workers=4,
        show_progress=show_progress,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        await orchestrator.add_tasks(tasks)
        await orchestrator.finish_tasks()
        job_results_1 = list(orchestrator.get_results())
        check.equal(len(job_results_1), 10)
        check.is_true(all(r.task.status == TaskState.fail for r in job_results_1))

        await orchestrator.add_tasks(tasks)
        await orchestrator.finish_tasks()
        job_results_2 = list(orchestrator.get_results())
        await orchestrator.stop_workers()
        check.equal(len(job_results_2), 10)
        check.is_true(all(r.task.status == TaskState.fail for r in job_results_2))


@pytest.mark.asyncio
@pytest.mark.parametrize("show_progress", [True, False])
async def test_stop_workers_with_no_added_tasks(logging_config, show_progress):
    async with Orchestrator(
        num_workers=4,
        show_progress=show_progress,
        logging_config=logging_config,
        actions={},
    ) as orchestrator:
        results = await orchestrator.stop_workers()
        check.equal(len(results), 0)


@pytest.mark.timeout(20)
@pytest.mark.asyncio
async def test_stop_workers_with_hanging_task(logging_config):
    """Verify `stop_workers` exits cleanly when an async task hangs."""
    test_actions = {hang_forever.action_name: hang_forever}
    async with Orchestrator(
        num_workers=2,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        await orchestrator.add_task(hang_forever())
        results = await orchestrator.stop_workers(timeout=10.0)
        # The main assertion is that `stop_workers` returns without the process hanging.
        # The hanging task is cancelled on shutdown, leading to one failed result.
        check.equal(len(results), 1)
        check.equal(results[0].task.status, TaskState.fail)


@pytest.mark.timeout(20)
@pytest.mark.asyncio
async def test_stop_workers_with_hanging_prop_initializer(logging_config):
    """Verify `stop_workers` terminates a worker stuck in async prop initialization."""
    config = {
        "props": {"hanging_prop": Prop(initializer=hang_initializer)},
    }
    async with Orchestrator(
        num_workers=1,
        show_progress=False,
        task_models=[Task],  # A model is needed, but task is never run
        logging_config=logging_config,
        actions={},
        **config,
    ) as orchestrator:
        # The worker process will hang on startup trying to initialize the prop.
        # We don't need to add any tasks. The test is whether `stop_workers`
        # can terminate the stuck process and return.
        results = await orchestrator.stop_workers(timeout=10.0)
        check.equal(
            len(results), 0, "No results should be returned from a hanging worker."
        )


@pytest.mark.asyncio
async def test_finish_tasks_concurrency(logging_config):
    """Verify `finish_tasks` only waits for tasks submitted before it was called."""
    test_actions = {sleep_then_finish.action_name: sleep_then_finish}
    async with Orchestrator(
        num_workers=2,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        # Batch 1: Fast tasks
        tasks1 = [sleep_then_finish(0.1) for _ in range(4)]
        await orchestrator.add_tasks(tasks1)

        # Create a task for finish_tasks, which is now async
        finish_task = asyncio.create_task(orchestrator.finish_tasks())

        # Give finish_tasks a moment to start
        await asyncio.sleep(0.1)

        # Batch 2: Slow tasks, added after finish_tasks is running
        tasks2 = [sleep_then_finish(5) for _ in range(2)]
        await orchestrator.add_tasks(tasks2)

        # The finish_task should complete long before the slow tasks.
        # A generous timeout to allow the fast tasks to complete.
        await asyncio.wait_for(finish_task, timeout=5.0)

        check.is_true(
            finish_task.done(),
            "finish_tasks should not wait for tasks added after it was called",
        )
        check.is_false(
            finish_task.cancelled(),
        )

        # Clean up
        await orchestrator.stop_workers()


@pytest.mark.asyncio
async def test_worker_responsiveness_with_retries(
    logging_config, conditional_fail_config
):
    """
    Verify that an idle worker waiting on a task promptly processes a scheduled retry.
    This tests the future-based blocking get with a calculated timeout.
    """
    config, attempt_tracker = conditional_fail_config
    retry_delay = 0.2  # A short but measurable delay
    test_actions = {fail_conditionally.action_name: fail_conditionally}

    async with Orchestrator(
        num_workers=1,  # Use a single worker to make timing predictable
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
        **config,
    ) as orchestrator:
        task_id = uuid4()
        task = fail_conditionally(
            str(task_id),  # task id
            2,  # succeed on 2nd attempt
            id=task_id,
            max_tries=2,
            initial_delay=retry_delay,
            backoff_strategy="simple",
        )

        start_time = time.monotonic()
        await orchestrator.add_task(task)
        results = await orchestrator.stop_workers()
        end_time = time.monotonic()

    duration = end_time - start_time

    # The task runs once, fails, waits for `retry_delay`, then runs again.
    # The total duration should be slightly more than the delay.
    # We allow a generous upper bound to account for overhead and CI slowness.
    check.greater_equal(duration, retry_delay)
    check.less(duration, retry_delay + 3.0, "Retry was not processed promptly.")

    check.equal(len(results), 1)
    result = results[0]
    check.equal(result.task.status, TaskState.success)
    check.equal(
        attempt_tracker.get(str(task.id)),
        2,
        "Action should have been executed twice.",
    )


@pytest.mark.asyncio
async def test_retry_on_evaluation_failure(logging_config, conditional_fail_config):
    """Verify a task is retried when its evaluator returns False, without an exception."""
    config, attempt_tracker = conditional_fail_config
    test_actions = {evaluate_conditionally.action_name: evaluate_conditionally}

    async with Orchestrator(
        num_workers=1,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
        **config,
    ) as orchestrator:
        task_id = uuid4()
        task = evaluate_conditionally(
            str(task_id),  # task id
            2,  # succeed on 2nd attempt
            id=task_id,
            max_tries=2,
            evaluator=is_ok_evaluator,
        )

        await orchestrator.add_task(task)
        results = await orchestrator.stop_workers()

    check.equal(len(results), 1)
    result = results[0]

    check.equal(result.task.status, TaskState.success)
    check.equal(result.result, "OK")
    retry_trait = next(
        t for t in result.task.traits if getattr(t, "trait_name", None) == "retryable"
    )
    check.equal(
        retry_trait.tries, 1, "Task should have been retried once before succeeding."
    )
    check.equal(
        attempt_tracker.get(str(task.id)),
        2,
        "Action should have been executed twice.",
    )


@pytest.mark.asyncio
async def test_retry_exhaustion(logging_config):
    """Verify a task fails permanently after exhausting all retries."""
    test_actions = {fail_action.action_name: fail_action}
    async with Orchestrator(
        num_workers=1,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        task = fail_action(
            max_tries=2,
            initial_delay=0.01,
        )

        await orchestrator.add_task(task)
        results = await orchestrator.stop_workers()

    check.equal(len(results), 1)
    result = results[0]

    # The task should have failed permanently
    check.equal(result.task.status, TaskState.fail)

    # The result should contain the exception info from the last attempt
    check.is_instance(result.result, list)
    check.is_instance(result.result[0], str)
    check.is_true("ErrorExpectedError" in result.result[0])

    # It should have been tried `max_tries` times after the initial attempt.
    retry_trait = next(
        t for t in result.task.traits if getattr(t, "trait_name", None) == "retryable"
    )
    check.equal(retry_trait.tries, 2)


@pytest.mark.asyncio
async def test_logging_writes_to_file(logging_config):
    """Verify that a worker's log call writes to the configured log file."""
    log_file_path = logging_config["log_file"]
    unique_message = f"test_log_message_{uuid4()}"
    test_actions = {log_a_message.action_name: log_a_message}

    async with Orchestrator(
        num_workers=1,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        task = log_a_message(unique_message, logging.WARNING)
        await orchestrator.add_task(task)
        await orchestrator.stop_workers()

    check.is_true(os.path.exists(log_file_path), "Log file was not created.")

    with open(log_file_path, "r") as f:
        log_content = f.read()

    check.is_in(
        unique_message,
        log_content,
        "The unique log message was not found in the log file.",
    )
    # Also check for some structure, like the log level name and pid
    check.is_in(
        "WARNING",
        log_content,
        "The log level was not found in the log file.",
    )
    check.is_in(
        "pid=",
        log_content,
        "The 'pid=' part of the structured log was not found.",
    )


@pytest.mark.asyncio
async def test_prop_initialization_failure(logging_config):
    """Verify the orchestrator remains stable when a prop fails to initialize."""
    test_actions = {use_prop.action_name: use_prop}
    async with Orchestrator(
        num_workers=1,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
        **orchestrator_configs["failing_prop"],
    ) as orchestrator:
        await orchestrator.add_task(use_prop())
        results = await orchestrator.stop_workers()
    # The orchestrator should not hang. The task should fail.
    check.equal(len(results), 1)
    check.equal(results[0].task.status, TaskState.fail)


@pytest.mark.asyncio
async def test_graceful_shutdown_with_many_tasks(logging_config):
    """Test that the orchestrator shuts down cleanly with a large number of tasks."""
    test_actions = {fail_action.action_name: fail_action}
    async with Orchestrator(
        num_workers=4,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        # Add a large number of tasks to the queue
        num_tasks = 1000
        tasks = [fail_action() for _ in range(num_tasks)]
        await orchestrator.add_tasks(tasks)

        # Immediately stop the workers. This should not hang.
        results = await orchestrator.stop_workers()

    check.equal(
        len(results), num_tasks, "All tasks should be processed or accounted for."
    )


@pytest.mark.asyncio
async def test_unpicklable_task_handling(logging_config):
    """Verify that unpicklable tasks are handled gracefully without hanging."""
    log_file_path = logging_config["log_file"]

    # This task is unpicklable because its evaluator is a lambda function.
    # The action doesn't matter, as the failure happens before execution.
    unpicklable_task = dummy_action_for_unpicklable(evaluator=lambda result: True)
    test_actions = {
        dummy_action_for_unpicklable.action_name: dummy_action_for_unpicklable,
        noop.action_name: noop,
    }

    async with Orchestrator(
        num_workers=1,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        failed_tasks = await orchestrator.add_tasks([unpicklable_task])

        # The unpicklable task should be returned as a failure.
        check.equal(len(failed_tasks), 1)
        check.is_in(unpicklable_task, failed_tasks)

        # The total task count should be 0, as it was never successfully added.
        check.equal(orchestrator.total_tasks, 0)

        # Ensure orchestrator can still process other valid tasks
        await orchestrator.add_task(noop())
        check.equal(orchestrator.total_tasks, 1)

        results = await orchestrator.stop_workers()

    # Only the valid NoopTask should have produced a result.
    check.equal(len(results), 1)

    # The log file should contain the specific error message.
    with open(log_file_path, "r") as f:
        log_content = f.read()

    check.is_in("Failed to enqueue task", log_content)
    check.is_in("The task or its payload is not picklable", log_content)
    check.is_in("Failed to serialize object", log_content)


@pytest.mark.asyncio
async def test_nested_function_task_handling(logging_config):
    """Verify that a task with a nested function evaluator is handled gracefully."""
    log_file_path = logging_config["log_file"]

    def nested_evaluator(result: Any) -> bool:
        """This function is not defined at the module's top level."""
        return result == "OK"

    unpicklable_task = dummy_action_for_unpicklable(evaluator=nested_evaluator)
    test_actions = {
        dummy_action_for_unpicklable.action_name: dummy_action_for_unpicklable
    }

    async with Orchestrator(
        num_workers=1,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        failed_tasks = await orchestrator.add_tasks([unpicklable_task])

        # The unpicklable task should be returned as a failure.
        check.equal(len(failed_tasks), 1)
        check.is_in(unpicklable_task, failed_tasks)

        # The total task count should be 0, as it was never successfully added.
        check.equal(orchestrator.total_tasks, 0)
        await orchestrator.stop_workers()

    # The log file should contain the specific error message.
    with open(log_file_path, "r") as f:
        log_content = f.read()

    check.is_in("Failed to enqueue task", log_content)
    check.is_in("The task or its payload is not picklable", log_content)
    check.is_in("Failed to serialize object", log_content)


@pytest.mark.asyncio
async def test_rate_limiting(logging_config):
    """Verify that the tasks_per_minute_limit is respected."""
    # Use a number of tasks greater than the per-minute limit to ensure
    # the rate-limiting logic is actually triggered.
    num_tasks = 130
    tasks_per_minute = 120  # 2 tasks per second
    # The first 120 tasks (60 per worker) execute in a burst. The remaining 10 tasks
    # are throttled at a combined rate of 2 tasks/sec, taking ~5 seconds.
    expected_duration_sec = (num_tasks - tasks_per_minute) / (tasks_per_minute / 60.0)
    test_actions = {noop.action_name: noop}

    async with Orchestrator(
        num_workers=2,  # Use more than 1 worker to test coordination
        show_progress=False,
        task_models=[Task],
        tasks_per_minute_limit=tasks_per_minute,
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        start_time = time.monotonic()
        await orchestrator.add_tasks([noop() for _ in range(num_tasks)])
        results = await orchestrator.stop_workers()
        end_time = time.monotonic()

    duration = end_time - start_time
    check.equal(len(results), num_tasks)

    # Allow for some timing variance and overhead, but check it's not too fast.
    # The rate limiter sleeps, so the time should be at least the expected duration.
    check.greater_equal(
        duration,
        expected_duration_sec * 0.9,
        f"Execution was too fast ({duration:.2f}s) for rate limit.",
    )


@pytest.mark.asyncio
async def test_retry_logic(logging_config, conditional_fail_config):
    """Verify that a task is retried on failure and eventually succeeds."""
    config, attempt_tracker = conditional_fail_config
    test_actions = {fail_conditionally.action_name: fail_conditionally}

    async with Orchestrator(
        num_workers=2,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
        **config,
    ) as orchestrator:
        task_id = uuid4()
        task = fail_conditionally(
            str(task_id),  # task id
            2,  # succeed on 2nd attempt
            id=task_id,
            max_tries=2,
        )

        await orchestrator.add_task(task)
        results = await orchestrator.stop_workers()

    check.equal(len(results), 1)
    result = results[0]

    check.equal(result.task.status, TaskState.success)
    check.equal(result.result, "Success")
    retry_trait = next(
        t for t in result.task.traits if getattr(t, "trait_name", None) == "retryable"
    )
    check.equal(
        retry_trait.tries, 1, "Task should have been retried once before succeeding."
    )
    check.equal(
        attempt_tracker.get(str(task.id)),
        2,
        "Action should have been executed twice.",
    )


def test_retryable_backoff_calculation():
    """Verify the exponential and simple backoff calculations are correct."""

    # --- Test exponential backoff (default) ---
    task_exp_instance = backoff_action(
        initial_delay=1,
        max_delay=10,
        max_tries=5,
        backoff_multiplier=2.0,
    )
    trait_exp = next(
        t
        for t in task_exp_instance.traits
        if getattr(t, "trait_name", None) == "retryable"
    )
    trait_exp.tries = 1
    check.equal(trait_exp.backoff(), 2.0)  # 1 * (2**1)
    trait_exp.tries = 2
    check.equal(trait_exp.backoff(), 4.0)  # 1 * (2**2)
    trait_exp.tries = 3
    check.equal(trait_exp.backoff(), 8.0)  # 1 * (2**3)
    trait_exp.tries = 4
    check.equal(trait_exp.backoff(), 10.0)  # Capped at max_delay (16.0 > 10.0)

    # --- Test simple backoff ---
    task_simple_instance = backoff_action(
        initial_delay=3,
        max_delay=10,
        max_tries=5,
        backoff_strategy="simple",
    )
    trait_simple = next(
        t
        for t in task_simple_instance.traits
        if getattr(t, "trait_name", None) == "retryable"
    )
    trait_simple.tries = 1
    check.equal(trait_simple.backoff(), 3.0)  # 3 * 1
    trait_simple.tries = 2
    check.equal(trait_simple.backoff(), 6.0)  # 3 * 2
    trait_simple.tries = 3
    check.equal(trait_simple.backoff(), 9.0)  # 3 * 3
    trait_simple.tries = 4
    check.equal(trait_simple.backoff(), 10.0)  # Capped at max_delay (12.0 > 10.0)


@pytest.mark.asyncio
async def test_add_task_and_add_tasks_counting(logging_config):
    """Verify that total_tasks is counted correctly across add_task and add_tasks."""
    test_actions = {noop.action_name: noop}
    async with Orchestrator(
        num_workers=1,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        await orchestrator.add_task(noop())
        check.equal(orchestrator.total_tasks, 1)

        await orchestrator.add_tasks([noop(), noop()])
        check.equal(orchestrator.total_tasks, 3)

        await orchestrator.add_task(noop())
        check.equal(orchestrator.total_tasks, 4)

        await orchestrator.stop_workers()


@pytest.mark.asyncio
async def test_get_results_multiple_calls(logging_config):
    """Verify get_results can be called multiple times and yields correct results."""
    test_actions = {sleep_then_finish.action_name: sleep_then_finish}
    async with Orchestrator(
        num_workers=2,
        show_progress=False,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        # First batch of tasks
        tasks1 = [sleep_then_finish(0.1) for _ in range(3)]
        await orchestrator.add_tasks(tasks1)
        await orchestrator.finish_tasks()

        results1 = list(orchestrator.get_results())
        check.equal(len(results1), 3)
        check.is_true(all(r.task.status == TaskState.success for r in results1))

        # Calling again should yield no new results
        results_empty = list(orchestrator.get_results())
        check.equal(
            len(results_empty), 0, "Calling get_results again should yield nothing"
        )

        # Second batch of tasks
        tasks2 = [sleep_then_finish(0.1) for _ in range(2)]
        await orchestrator.add_tasks(tasks2)
        await orchestrator.finish_tasks()

        results2 = list(orchestrator.get_results())
        check.equal(len(results2), 2)
        check.is_true(all(r.task.status == TaskState.success for r in results2))

        # Clean up
        await orchestrator.stop_workers()


@pytest.mark.asyncio
@patch("wombat.multiprocessing.progress.Progress")
async def test_progress_bar_correctness_of_counts(
    mock_progress_class: MagicMock, logging_config, conditional_fail_config
):
    """Verify progress bar correctly counts completed, failed, and retried tasks."""
    mock_progress_instance = mock_progress_class.return_value
    # Make add_task return predictable, sequential IDs for workers and the total bar
    num_workers = 2
    mock_progress_instance.add_task.side_effect = range(num_workers + 1)
    total_task_id = num_workers  # The "Total" bar is added after the worker bars

    # --- Setup Tasks for mixed outcomes ---
    succeeding_tasks = [noop() for _ in range(2)]
    failing_tasks = [fail_action(max_tries=0) for _ in range(3)]

    config, _ = conditional_fail_config
    task_id = uuid4()
    retry_task = fail_conditionally(
        str(task_id),  # task_id arg
        2,  # succeed on try 2
        id=task_id,
        max_tries=1,
        initial_delay=0.01,
    )
    all_tasks = succeeding_tasks + failing_tasks + [retry_task]
    test_actions = {
        noop.action_name: noop,
        fail_action.action_name: fail_action,
        fail_conditionally.action_name: fail_conditionally,
    }

    # --- Configure and run Orchestrator ---
    async with Orchestrator(
        num_workers=num_workers,
        show_progress=True,
        task_models=[Task],
        logging_config=logging_config,
        actions=test_actions,
        **config,
    ) as orchestrator:
        await orchestrator.add_tasks(all_tasks)
        await orchestrator.stop_workers()

    # --- Assert correctness of the final progress bar state ---
    # Aggregate all keyword arguments for the 'Total' progress bar updates.
    final_state = {}
    for call in mock_progress_instance.update.call_args_list:
        args, kwargs = call
        if args[0] == total_task_id:
            final_state.update(kwargs)

    # Expected: 2 NoopTasks + 1 RetryTask = 3 completed
    check.equal(final_state.get("completed"), 3)
    # Expected: 3 Fail tasks = 3 failures
    check.equal(final_state.get("failures"), 3)
    # Expected: 1 retry from the ConditionalFailTask
    check.equal(final_state.get("retries"), 1)


@pytest.mark.asyncio
async def test_on_before_execute_prevents_execution(logging_config):
    """Verify that on_before_execute returning False prevents a task from running."""
    # Clean up any leftover file from a previous failed run
    if os.path.exists("test_on_before_execute.tmp"):
        os.remove("test_on_before_execute.tmp")

    test_actions = {
        expired_action.action_name: expired_action,
        noop.action_name: noop,
    }
    async with Orchestrator(
        num_workers=1,
        show_progress=False,
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        expiring_task = expired_action()
        normal_task = noop()

        await orchestrator.add_tasks([expiring_task, normal_task])
        results = await orchestrator.stop_workers()

    check.equal(len(results), 2, "Should receive results for both tasks.")

    expired_result = next(r for r in results if r.task.id == expiring_task.id)
    normal_result = next(r for r in results if r.task.id == normal_task.id)

    check.equal(expired_result.task.status, TaskState.expire)
    check.is_in("skipped by pre-flight hook", expired_result.result)

    check.equal(normal_result.task.status, TaskState.success)

    check.is_false(
        os.path.exists("test_on_before_execute.tmp"),
        "Expired task's action should not have been executed.",
    )

    # Final cleanup
    if os.path.exists("test_on_before_execute.tmp"):
        os.remove("test_on_before_execute.tmp")


@pytest.mark.asyncio
async def test_decorator_defined_task(logging_config):
    """Verify that a task defined with the @task decorator executes correctly."""
    # The decorator automatically registers the action, so no 'actions' dict is needed for it.
    test_actions = {
        tests.helpers.decorated_task_action.action_name: tests.helpers.decorated_task_action
    }
    async with Orchestrator(
        num_workers=1,
        show_progress=False,
        logging_config=logging_config,
        actions=test_actions,
    ) as orchestrator:
        # Create a task instance by calling the wrapped function
        task_instance = tests.helpers.decorated_task_action(5, 10)
        await orchestrator.add_task(task_instance)
        results = await orchestrator.stop_workers()

    check.equal(len(results), 1)
    result = results[0]

    check.equal(result.task.status, TaskState.success)
    check.equal(result.result, 15)
    # Check that the action name was correctly inferred
    check.is_in("decorated_task_action", result.task.action)
