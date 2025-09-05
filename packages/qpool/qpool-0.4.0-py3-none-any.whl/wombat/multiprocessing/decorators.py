# File: src/wombat/multiprocessing/decorators.py
from __future__ import annotations

import functools
import inspect
from typing import TYPE_CHECKING, Any, Callable, Type

from wombat.multiprocessing.models import (
    TRAIT_REGISTRY,
    BaseTrait,
    EvaluatableTrait,
    ExpirableTrait,
    LoggableTrait,
    ProgressTrait,
    RequiresPropsTrait,
    RetryableTrait,
    Task,
)

if TYPE_CHECKING:
    from wombat.multiprocessing.models import Task


def register_trait_decorator(trait_cls: Type[BaseTrait]) -> Callable:
    """
    Registers a trait class and creates its corresponding decorator function.
    """
    if "trait_name" in trait_cls.model_fields:
        trait_name_field = trait_cls.model_fields["trait_name"]
        if hasattr(trait_name_field.annotation, "__args__"):
            trait_name = trait_name_field.annotation.__args__[0]
            TRAIT_REGISTRY[trait_name] = trait_cls
            return _create_trait_decorator(trait_name, trait_cls)
    raise TypeError(
        f"Trait class {trait_cls.__name__} must have a 'trait_name: Literal[\"...\"]' field."
    )


def task() -> Callable[[Callable], Callable[..., Task]]:
    """
    A decorator to transform a function into a Wombat task definition.

    Note: For a decorated function to be usable by worker processes, it must be
    defined at the top level of a module. Defining tasks inside other functions
    or as lambda functions is not supported, as they cannot be reliably sent
    to other processes.
    """

    def decorator(func: Callable) -> Callable[..., Task]:
        if hasattr(func, "action_name") and hasattr(func, "capabilities"):
            return func  # Already a task factory

        action_name = f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def task_factory(*args: Any, **kwargs: Any) -> Task:
            """Creates a new Pydantic Task model instance for the decorated function."""
            # Separate kwargs for the Task model, traits, and the action function.
            task_model_fields = Task.model_fields.keys()
            all_trait_fields = set()
            for capability_name in task_factory.capabilities:
                if capability_name in TRAIT_REGISTRY:
                    all_trait_fields.update(
                        TRAIT_REGISTRY[capability_name].model_fields.keys()
                    )

            model_kwargs = {k: v for k, v in kwargs.items() if k in task_model_fields}
            action_kwargs = {
                k: v
                for k, v in kwargs.items()
                if k not in task_model_fields and k not in all_trait_fields
            }

            task_data = {
                "action": task_factory.action_name,
                "args": list(args),
                "kwargs": action_kwargs,
                "traits": [],
                **model_kwargs,
            }

            for k, v in task_factory.options.items():
                if k in task_model_fields:
                    task_data[k] = v

            for capability_name in task_factory.capabilities:
                if capability_name in TRAIT_REGISTRY:
                    TraitModel = TRAIT_REGISTRY[capability_name]
                    trait_data = {"trait_name": capability_name}
                    decorator_options = {
                        k: v
                        for k, v in task_factory.options.items()
                        if k in TraitModel.model_fields
                    }
                    trait_data.update(decorator_options)
                    new_call_kwargs = {
                        k: v for k, v in kwargs.items() if k in TraitModel.model_fields
                    }
                    trait_data.update(new_call_kwargs)
                    task_data["traits"].append(trait_data)

            return Task(**task_data)

        task_factory.action_name = action_name
        task_factory.capabilities = set()
        task_factory.options = {}
        task_factory.func = func
        return task_factory

    return decorator


def _create_trait_decorator(
    name: str, trait_model: Type[BaseTrait]
) -> Callable[..., Callable[[Callable], Callable[..., Task]]]:
    """Factory to create decorators for traits."""
    params = []
    for field_name, field_info in trait_model.model_fields.items():
        if field_name in ["trait_name", "tries"]:  # Exclude fields not set by user
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

    signature = inspect.Signature(params)

    def decorator_factory(**kwargs) -> Callable[[Callable], Callable[..., Task]]:
        def decorator(func: Callable) -> Callable[..., Task]:
            if hasattr(func, "action_name") and hasattr(func, "capabilities"):
                factory = func
            else:
                # If @task is missing, add a default one.
                factory = task()(func)

            factory.capabilities.add(name)
            factory.options.update(kwargs)
            return factory

        return decorator

    decorator_factory.__name__ = name
    decorator_factory.__signature__ = signature
    return decorator_factory


# Create all built-in decorators so they are statically available for import.
retryable = register_trait_decorator(RetryableTrait)
evaluatable = register_trait_decorator(EvaluatableTrait)
expirable = register_trait_decorator(ExpirableTrait)
loggable = register_trait_decorator(LoggableTrait)
progress = register_trait_decorator(ProgressTrait)
requires_props = register_trait_decorator(RequiresPropsTrait)
