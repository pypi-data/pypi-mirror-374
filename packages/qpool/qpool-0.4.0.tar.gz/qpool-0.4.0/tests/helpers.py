from __future__ import annotations

from typing import TYPE_CHECKING

from wombat.multiprocessing import evaluatable, requires_props, retryable, task
from wombat.multiprocessing.models import Prop

if TYPE_CHECKING:
    from wombat.multiprocessing.worker import Worker


class ErrorExpectedError(Exception):
    pass


@task()
def decorated_task_action(_worker: Worker, x: int, y: int) -> int:
    """A simple action defined via decorator for testing."""
    return x + y


@task()
@retryable()
def fail_action(_worker: "Worker"):
    """An action that raises a predictable exception for testing."""
    raise ErrorExpectedError


@task()
@retryable()
@requires_props(requires_props=["attempt_tracker", "lock"])
def fail_conditionally(
    _worker: Worker, task_id: str, succeed_on_try: int, props: dict[str, Prop]
):
    """
    Action that fails until a certain attempt number is reached.
    Uses a shared dictionary (from a multiprocessing.Manager) to track attempts.
    """
    tracker = props["attempt_tracker"].instance
    lock = props["lock"].instance

    with lock:
        current_attempt = tracker.get(task_id, 0)
        tracker[task_id] = current_attempt + 1

    if current_attempt < succeed_on_try - 1:
        error = f"Failing on attempt {current_attempt + 1}"
        raise ValueError(error)
    return "Success"


@task()
@retryable()
@evaluatable()
@requires_props(requires_props=["attempt_tracker", "lock"])
def evaluate_conditionally(
    _worker: Worker, task_id: str, succeed_on_try: int, props: dict[str, Prop]
):
    """
    Action that returns a failure value until a certain attempt is reached.
    Does not raise an exception.
    """
    tracker = props["attempt_tracker"].instance
    lock = props["lock"].instance

    with lock:
        current_attempt = tracker.get(task_id, 0)
        tracker[task_id] = current_attempt + 1

    if current_attempt < succeed_on_try - 1:
        return "ERROR"
    return "OK"
