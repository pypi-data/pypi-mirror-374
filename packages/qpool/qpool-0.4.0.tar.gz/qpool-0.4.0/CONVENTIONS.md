# Coding conventions

1. Never use timeouts unless they are specifically set to be when you NEED to wake up.
2. No busy-waits.
3. Always run the code using `PYTHONPATH="" uv run --python 3.13.5 pytest -x -k {the test name you care about}` or `PYTHONPATH="" uv run --python 3.13.5 pytest -x` for all tests.
4. Never use pickle, cPickle, or any variant thereof.
5. Never write dirty hacks or workarounds, design and architect robust solutions.
6. Never use polling, only use event-driven code.