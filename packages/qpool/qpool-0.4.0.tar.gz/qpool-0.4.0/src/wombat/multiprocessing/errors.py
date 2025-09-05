class UnpicklablePayloadError(TypeError):
    """Raised when a task or its payload cannot be serialized for multiprocessing."""

    pass


class WorkerCrashError(RuntimeError):
    """Raised when a worker process terminates unexpectedly."""

    pass


class EvaluationFailureError(ValueError):
    """Raised when a task's result fails a post-execution evaluation check."""

    pass
