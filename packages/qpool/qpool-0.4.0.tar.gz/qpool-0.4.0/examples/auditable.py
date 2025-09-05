import asyncio
import logging
from typing import Any, Literal

from wombat.multiprocessing.models import BaseTrait, Task
from wombat.multiprocessing.orchestrator import Orchestrator
from wombat.multiprocessing.worker import Worker


# 1. Define your custom trait.
class AuditableTrait(BaseTrait):
    """A custom trait to log a message before and after execution."""

    trait_name: Literal["auditable"] = "auditable"
    audit_message: str

    def on_before_execute(self, task: "Task", worker: "Worker") -> bool:
        worker.log(
            f"AUDIT START: {self.audit_message} for task {task.id}", logging.INFO
        )
        return True

    def on_success(self, task: "Task", worker: "Worker", result: Any):
        worker.log(f"AUDIT END: Task {task.id} completed successfully.", logging.INFO)


# Import the registration function and the base task decorator.
from wombat.multiprocessing import register_trait_decorator, task  # noqa: E402

# 2. Register the custom trait to create its decorator.
auditable = register_trait_decorator(AuditableTrait)


# 3. Define a task that uses your new decorator.
@task()
@auditable(audit_message="Performing important calculation")
def add_numbers(_worker: Worker, x: int, y: int) -> int:
    """A simple task that adds two numbers."""
    return x + y


# 4. Use the Orchestrator to run the task (no `actions` dict needed).
async def main():
    # Configure logging to see the audit messages in the console.
    logging_config = {"to_console": True, "level": logging.INFO}

    # The actions dictionary maps the task's action name to the function.
    test_actions = {add_numbers.action_name: add_numbers}

    async with Orchestrator(
        num_workers=2, logging_config=logging_config, actions=test_actions
    ) as orchestrator:
        # Create a task instance.
        task_instance = add_numbers(5, 10)

        # Add the task to the pool.
        await orchestrator.add_task(task_instance)

        # Wait for the task to complete and get the results.
        results = await orchestrator.stop_workers()
        print(f"\nTask result: {results[0].result}")


if __name__ == "__main__":
    asyncio.run(main())
