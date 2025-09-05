# File: src/wombat/multiprocessing/queues.py
from __future__ import annotations

import importlib
import inspect
from datetime import date, datetime, timedelta
from enum import Enum
from multiprocessing import JoinableQueue, Queue
from multiprocessing.context import BaseContext
from queue import Empty
from typing import Callable, List, Optional, Type, TypeVar, Union
from uuid import UUID

import msgpack
from pydantic import BaseModel

from wombat.multiprocessing.errors import UnpicklablePayloadError
from wombat.multiprocessing.models import ResultTaskPair
from wombat.multiprocessing.models import LoggableTrait, Task
from wombat.utils.errors.decorators import enforce_type_hints_contracts

T = TypeVar("T", bound=BaseModel)


def default_encoder(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, timedelta):
        return obj.total_seconds()
    if isinstance(obj, Enum):
        return obj.value
    if callable(obj) and inspect.isfunction(obj):
        if obj.__name__ == "<lambda>":
            raise TypeError("Lambda functions are not serializable")
        if "<locals>" in obj.__qualname__:
            raise TypeError("Nested functions are not serializable")
        return f"{obj.__module__}.{obj.__name__}"
    raise TypeError(f"Object of type {type(obj).__name__} is not serializable")


def explicitly_is(item: BaseModel, models: List[Type[BaseModel]]) -> bool:
    return any([item.__class__ == model for model in models])


def implicitly_is(item: BaseModel, models: List[Type[BaseModel]]) -> bool:
    return any([isinstance(item, model) for model in models])


class ModelQueue:
    name: str
    joinable: bool = False
    queue: Union[JoinableQueue, Queue]
    models: List[Type[BaseModel]]
    validator: Callable[[BaseModel, List[Type[BaseModel]]], bool]
    context: BaseContext

    def __init__(
        self,
        context: BaseContext,
        name: str,
        models: List[Type[BaseModel]],
        joinable: bool = False,
        validator: Optional[
            Callable[[BaseModel, List[Type[BaseModel]]], bool]
        ] = explicitly_is,
    ):
        self.context = context
        self.name = name
        self.joinable = joinable
        self.validator = validator
        self.models = models
        # Unbounded by default (maxsize == 0): preserves all messages (lossless).
        self.queue = self.context.JoinableQueue() if joinable else self.context.Queue()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.join()

    def _pack(self, item: BaseModel) -> bytes:
        return msgpack.packb(
            {
                "type": f"{item.__class__.__module__}.{item.__class__.__name__}",
                "data": item.model_dump(mode="python"),
            },
            default=default_encoder,
            use_bin_type=True,
        )

    def _unpack(self, packed_item: bytes) -> BaseModel:
        unpacked = msgpack.unpackb(packed_item, raw=False)
        data = unpacked["data"]
        type_str = unpacked["type"]

        # The Task model with discriminated union on traits handles reconstruction.
        module_name, class_name = type_str.rsplit(".", 1)
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        return cls.model_validate(data)

    def put(self, item: T, block: bool = True, timeout: Optional[float] = None) -> bool:
        if not self.validator(item, self.models):
            return False
        try:
            # Pre-serialize the object to catch serialization errors before they
            # can crash the queue's background feeder thread.
            packed_item = self._pack(item)
            self.queue.put(packed_item, block=block, timeout=timeout)
            return True
        except (TypeError, AttributeError) as e:
            # AttributeError is raised for unpicklable local functions (lambdas)
            raise UnpicklablePayloadError(
                f"Failed to serialize object of type {type(item).__name__} for queue '{self.name}'."
            ) from e
        except Exception:
            # For other queue errors (e.g., Full with block=False), maintain original behavior
            return False

    def get(self, block: bool = True, timeout: Optional[float] = None) -> BaseModel:
        packed_item = self.queue.get(block, timeout)
        return self._unpack(packed_item)

    def task_done(self):
        if not self.joinable:
            return
        self.queue.task_done()

    def join(self):
        if self.joinable:
            self.queue.join()
        else:
            self.queue.join_thread()

    def empty(self):
        return self.queue.empty()

    def full(self):
        return self.queue.full()

    def get_nowait(self) -> BaseModel:
        packed_item = self.queue.get_nowait()
        return self._unpack(packed_item)

    def put_nowait(self, obj):
        packed_item = self._pack(obj)
        return self.queue.put_nowait(packed_item)

    def close(self):
        return self.queue.close()


def log_task(
    task: Task,
    message: str,
    queue: Optional[ModelQueue] = None,
    level: Optional[int] = None,
):
    """Log a message to the provided queue (lossless; the queue itself is unbounded)."""
    if not queue:
        return

    # A task is loggable if it has the LoggableTrait.
    loggable_trait = next(
        (
            trait
            for trait in getattr(task, "traits", [])
            if isinstance(trait, LoggableTrait)
        ),
        None,
    )

    if not loggable_trait:
        # Task is not configured to be loggable.
        return

    final_log_level = level if level is not None else loggable_trait.log_level

    log_task_instance = Task(
        action="log",
        traits=[{"trait_name": "requires_props", "requires_props": ["logger"]}],
        kwargs={
            "message": message,
            "level": final_log_level,
        },
    )
    queue.put(log_task_instance)


@enforce_type_hints_contracts
def TaskQueue(
    context: BaseContext,
    name: str,
    joinable: bool = True,
    models: List[Type[Task]] = None,
) -> ModelQueue:
    models = models or [Task]
    return ModelQueue(
        context=context,
        name=name,
        models=models,
        joinable=joinable,
        validator=implicitly_is,
    )


@enforce_type_hints_contracts
def ProgressQueue(
    context: BaseContext, name: str, joinable: bool = True, validator=explicitly_is
) -> ModelQueue:
    return ModelQueue(
        context=context,
        name=name,
        models=[Task],
        joinable=joinable,
        validator=validator,
    )


@enforce_type_hints_contracts
def ControlQueue(
    context: BaseContext, name: str, joinable: bool = True, validator=implicitly_is
) -> ModelQueue:
    return ModelQueue(
        context=context,
        name=name,
        models=[Task],
        joinable=joinable,
        validator=validator,
    )


@enforce_type_hints_contracts
def ResultQueue(context: BaseContext, name: str, joinable: bool = False) -> ModelQueue:
    return ModelQueue(
        context=context, name=name, models=[ResultTaskPair], joinable=joinable
    )


@enforce_type_hints_contracts
def LogQueue(context: BaseContext, name: str, joinable: bool = True) -> ModelQueue:
    # Unbounded queue: prevents log loss by design (at the cost of possible mem growth).
    return ModelQueue(context=context, name=name, models=[Task], joinable=joinable)


@enforce_type_hints_contracts
def drain_queue_non_blocking(model_queue: ModelQueue) -> List[BaseModel]:
    """Drains a queue of all currently available items, without blocking."""
    results = []
    while True:
        try:
            result: BaseModel = model_queue.get(block=False)
            if model_queue.joinable:
                model_queue.task_done()
            results.append(result)
        except Empty:
            break  # The queue is empty, so we're done.
    return results


