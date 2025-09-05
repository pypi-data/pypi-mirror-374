# File: src/wombat/multiprocessing/models.py
"""This file contains the models that we composite to represent our Tasks and their behaviors."""

from __future__ import annotations

import importlib
import inspect
import logging
from contextlib import AsyncExitStack
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Type,
    TypeVar,
)
from uuid import uuid4

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic_partial import create_partial_model

from wombat.multiprocessing.errors import EvaluationFailureError
from wombat.utils.errors.decorators import enforce_type_hints_contracts


def create_capability_decorator(
    name: str, model: Type[BaseModel], excluded_args: Optional[List[str]] = None
) -> Callable:
    """
    Dynamically creates a decorator for a given capability using `inspect`.
    """
    excluded_args = excluded_args or []
    params = []

    for field_name, field_info in model.model_fields.items():
        if field_name in excluded_args:
            continue

        default = inspect.Parameter.empty
        if field_info.default is not ...:
            default = field_info.default

        params.append(
            inspect.Parameter(
                name=field_name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                default=default,
                annotation=field_info.annotation,
            )
        )

    signature = inspect.Signature(
        params, return_annotation="Callable[[Callable[..., Task]], Callable[..., Task]]"
    )

    def decorator_factory(
        **kwargs,
    ) -> Callable[[Callable[..., Task]], Callable[..., Task]]:
        """Auto-generated decorator for the '{name}' capability."""

        def decorator(factory: Callable[..., Task]) -> Callable[..., Task]:
            # Duck-typing check to avoid circular import at runtime.
            if not (hasattr(factory, "capabilities") and hasattr(factory, "options")):
                raise TypeError(f"@{name} must be stacked on top of a @task decorator.")
            factory.capabilities.add(name)
            filtered_options = {k: v for k, v in kwargs.items() if v is not None}
            factory.options.update(filtered_options)
            return factory

        return decorator

    decorator_factory.__name__ = name
    decorator_factory.__doc__ = f"Auto-generated decorator for the '{name}' capability."
    decorator_factory.__signature__ = signature

    return decorator_factory


def utc_datetime() -> datetime:
    """Return the current time with UTC timezone."""
    return datetime.now(UTC)


if TYPE_CHECKING:
    from multiprocessing.sharedctypes import Synchronized

    from wombat.multiprocessing.queues import ModelQueue
    from wombat.multiprocessing.worker import Worker


@enforce_type_hints_contracts
def simple_backoff(
    retries: int, initial_delay: float | int, max_delay: float | int
) -> float:
    """Simple backoff function. Same delay for each retry until max_delay is reached."""
    return min(max_delay, initial_delay * retries)


@enforce_type_hints_contracts
def exponential_backoff(
    retries: int,
    initial_delay: float | int,
    max_delay: float | int,
    multiplier: float | int,
) -> float:
    """Exponential backoff function. Delay increases exponentially with each retry until max_delay is reached."""
    return min(max_delay, initial_delay * (multiplier**retries))


class BaseTrait(BaseModel):
    """Base class for all task traits, defining the lifecycle hook interface."""

    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True,
    )

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    def on_before_execute(self, task: "Task", worker: "Worker") -> bool:
        """
        Hook executed before the task's action is run.
        Return False to prevent execution.
        """
        return True

    def on_success(self, task: "Task", worker: "Worker", result: Any):
        """Hook executed after the task's action runs successfully."""
        pass

    def on_failure(
        self, task: "Task", worker: "Worker", exception: Exception | str | None
    ):
        """Hook executed when the task's action raises an exception."""
        pass


class ExpirableTrait(BaseTrait):
    """Trait that adds expiration behavior to a task."""

    trait_name: Literal["expirable"] = "expirable"
    created_at: datetime = Field(default_factory=utc_datetime, exclude=True)
    expires_at: Optional[datetime] = Field(
        default=None, description="The UTC timestamp when the task expires."
    )
    expires_after: Optional[timedelta] = Field(
        default=None,
        description="The duration after creation when the task expires.",
        exclude=True,
    )

    @model_validator(mode="after")
    def set_expires_at_from_duration(self) -> "ExpirableTrait":
        if self.expires_after and self.expires_at:
            raise ValueError("Provide 'expires_at' or 'expires_after', not both.")
        if self.expires_after:
            self.expires_at = self.created_at + self.expires_after
        return self

    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return utc_datetime() >= self.expires_at

    def on_before_execute(self, task: "Task", worker: "Worker") -> bool:
        """Hook to check for expiration before execution."""
        if self.is_expired():
            worker.log(
                f"Task {getattr(task, 'id', 'N/A')} expired and was skipped.",
                logging.INFO,
            )
            task.status = TaskState.expire
            return False  # Prevent execution
        return True


class RetryableTrait(BaseTrait):
    """Trait that adds retry behavior to a task."""

    trait_name: Literal["retryable"] = "retryable"
    tries: int = Field(
        ge=0,
        default=0,
        description="The number of times the task has been attempted after the initial one.",
    )
    max_tries: int = Field(
        ge=0,
        default=3,
        description="The maximum number of times the task can be retried.",
    )
    initial_delay: float = Field(
        ge=0.0, default=2, description="The initial delay before the first retry."
    )
    max_delay: float = Field(
        ge=0.0, default=60.0, description="The maximum delay between retries."
    )
    backoff_strategy: Literal["exponential", "simple"] = Field(
        default="exponential",
        description="The backoff strategy to use for retries ('exponential' or 'simple').",
    )
    backoff_multiplier: float = Field(
        default=2.0,
        ge=1.0,
        description="The multiplier to use for exponential backoff. Must be >= 1.",
    )

    def on_failure(
        self, task: "Task", worker: "Worker", exception: Exception | str | None
    ):
        worker.log(
            f"DEBUG_TRIES: on_failure for task {getattr(task, 'id', 'N/A')}: tries BEFORE increment is {self.tries}",
            logging.DEBUG,
        )
        if self.tries < self.max_tries:
            self.tries += 1
            worker.log(
                f"DEBUG_TRIES: on_failure for task {getattr(task, 'id', 'N/A')}: tries AFTER increment is {self.tries}. Setting status to retry.",
                logging.DEBUG,
            )
            task.status = TaskState.retry
        else:
            worker.log(
                f"DEBUG_TRIES: on_failure for task {getattr(task, 'id', 'N/A')}: max_tries reached. Tries is {self.tries}. Setting status to fail.",
                logging.DEBUG,
            )
            task.status = TaskState.fail

    def backoff(self) -> float:
        """Calculates the backoff delay for the next retry attempt."""
        if self.backoff_strategy == "simple":
            return simple_backoff(self.tries, self.initial_delay, self.max_delay)

        return exponential_backoff(
            self.tries, self.initial_delay, self.max_delay, self.backoff_multiplier
        )


class EvaluatableTrait(BaseTrait):
    """Trait that adds result evaluation to a task."""

    trait_name: Literal["evaluatable"] = "evaluatable"
    evaluator: Optional[Callable[[Any], bool]] = None

    @field_validator("evaluator", mode="before")
    @classmethod
    def _validate_evaluator(cls, v: Any) -> Optional[Callable[[Any], bool]]:
        if isinstance(v, str):
            try:
                module_name, func_name = v.rsplit(".", 1)
                module = importlib.import_module(module_name)
                func = getattr(module, func_name)
                if not callable(func):
                    raise ValueError(f"'{v}' is not a callable.")
                return func
            except (ValueError, ImportError, AttributeError) as e:
                raise ValueError(f"Could not import evaluator '{v}'.") from e
        return v

    def on_success(self, task: "Task", worker: "Worker", result: Any):
        if not self.evaluate(result):
            # Dispatch to on_failure hooks of other traits (like RetryableTrait).
            exc = EvaluationFailureError(f"Evaluation failed for result: {result!r}")
            for trait in task.traits:
                trait.on_failure(task, worker, exc)
        else:
            task.status = TaskState.success

    def evaluate(self, data: Any) -> bool:
        return self.evaluator(data) if self.evaluator else True


class LoggableTrait(BaseTrait):
    """Trait that adds logging behavior to a task."""

    trait_name: Literal["loggable"] = "loggable"
    log_level: int = logging.INFO


class ProgressTrait(BaseTrait):
    """Trait that adds progress tracking behavior to a task."""

    trait_name: Literal["progress"] = "progress"
    weight: int = Field(ge=0, default=1)


class RequiresPropsTrait(BaseTrait):
    """Trait that specifies which props a task requires."""

    trait_name: Literal["requires_props"] = "requires_props"
    requires_props: List[str] = Field(
        default_factory=list,
        description="A list of required props that the task expects to be passed to it.",
    )
    include_all_props: bool = Field(
        default=False,
        description="Whether to include all props in the kwargs passed to the task.",
    )


# A registry to map capability names to their Trait models.
TRAIT_REGISTRY: dict[str, Type["BaseTrait"]] = {}


class ResultTaskPair(BaseModel):
    """This represents a tuple of a task and a result."""

    task: "Task | Sentinel"
    result: Any

    def __init__(self, task: "Task | Sentinel", result: Any) -> None:
        """
        Safety: never mutate the original task instance. Build a sanitized copy
        that removes kwargs['props'] if present, so results are serializable and
        free of giant cross-process references.
        """
        safe_task = task
        try:
            # If we have a subclass of Task, convert it to a base Task instance
            # to prevent Pydantic serialization warnings.
            if isinstance(task, Task) and type(task) is not Task:
                task = Task.model_validate(task.model_dump())

            if isinstance(task, Task):
                # Use `model_copy` to ensure an exact replica of the task's state,
                # including mutated fields like `tries`. Then, sanitize the copy.
                safe_task = task.model_copy(deep=True)
                if hasattr(safe_task, "kwargs") and isinstance(safe_task.kwargs, dict):
                    safe_task.kwargs.pop("props", None)
            else:
                safe_task = task
        except Exception:
            # If reconstruction fails, fall back to the original task. Better to return
            # something with potentially un-serializable props than to crash the worker.
            safe_task = task
        super().__init__(task=safe_task, result=result)

    def __str__(self) -> str:
        return f"{self.task} => {self.result}"


class Trackable(BaseModel):
    path: List[str]

    def track(self, action: str):
        self.path.append(action)


class Sentinel(BaseModel):
    """Mixin that provides a sentinel field for tasks that should not be executed."""

    sentinel: str


class TaskState(Enum):
    """Enumeration of possible task states over the course of a Task lifecycle."""

    create = "create"
    queue = "queue"
    attempt = "attempt"
    retry = "retry"
    fail = "fail"
    success = "success"
    expire = "expire"
    cancel = "cancel"


class Task(BaseModel):
    """The core task model, using composition for all behaviors."""

    id: UUID4 = Field(default_factory=lambda: uuid4())
    action: str = Field(
        ...,
        description="The action to be performed by the task. Expected to map to a key in the Workers Action dictionary.",
    )
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    status: TaskState = Field(
        default=TaskState.create, description="The current status of the task."
    )
    traits: list[Any] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _instantiate_traits(cls, data: Any) -> Any:
        if isinstance(data, dict):
            instantiated_traits = []
            if "traits" in data and data["traits"]:
                for trait_data in data["traits"]:
                    if isinstance(trait_data, BaseTrait):
                        instantiated_traits.append(trait_data)
                        continue
                    if isinstance(trait_data, dict):
                        trait_name = trait_data.get("trait_name")
                        if trait_name in TRAIT_REGISTRY:
                            TraitModel = TRAIT_REGISTRY[trait_name]
                            instantiated_traits.append(TraitModel(**trait_data))
                        else:
                            # If trait is unknown, keep it as a dict and let
                            # downstream validation handle it if necessary.
                            instantiated_traits.append(trait_data)
                    else:
                        instantiated_traits.append(trait_data)
                data["traits"] = instantiated_traits
        return data

    def filter_props(self, props: Dict[str, Prop]) -> Dict[str, Any]:
        req_props_trait = next(
            (trait for trait in self.traits if isinstance(trait, RequiresPropsTrait)),
            None,
        )

        if not req_props_trait:
            return {}

        if req_props_trait.include_all_props:
            return props
        return {k: v for k, v in props.items() if k in req_props_trait.requires_props}


class EOQ(Sentinel):
    sentinel: str = "EOQ"


T = TypeVar("T")


class Prop(BaseModel):
    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True,
    )
    initializer: Any | Callable[[], Any] = Field(
        description="The function that initializes the prop. MUST BE PICKLABLE."
    )
    instance: Any = Field(
        description="The resolved instance of the prop.", default=None
    )
    exit_stack: Optional[AsyncExitStack] = Field(
        description="The exit stack managing the prop's context.", default=None
    )
    use_context_manager: bool = Field(
        description="Whether the prop should be used as a context manager.",
        default=True,
    )


UninitializedProp = create_partial_model(Prop, "instance")


class WorkerConfig(BaseModel):
    model_config: ConfigDict = ConfigDict(
        arbitrary_types_allowed=True,
    )
    context: Any
    name: str
    worker_id: UUID4
    task_id: int
    packed_actions: bytes
    props: Dict[str, Prop]
    control_queues: Dict[str, "ModelQueue"]
    task_queue: "ModelQueue"
    result_queue: Optional["ModelQueue"]
    log_queue: Optional["ModelQueue"]
    progress_queue: Optional["ModelQueue"]
    status: "Synchronized"
    finished_tasks: Optional["Synchronized"] = None
    total_progress_tasks: Optional["Synchronized"]
    tasks_per_minute_limit: Optional["Synchronized"]
    max_concurrent_tasks: Optional[int]


class ProgressUpdate(BaseModel):
    task_id: int
    total: int = 0
    completed: int = 0
    elapsed: float = 0.0
    remaining: float = 0.0
    failures: int = 0
    retries: int = 0
    status: str = "created"


# Late imports to resolve forward references and avoid circular dependencies.
from multiprocessing.sharedctypes import Synchronized  # noqa: E402

from wombat.multiprocessing.queues import ModelQueue  # noqa: E402

WorkerConfig.model_rebuild()
