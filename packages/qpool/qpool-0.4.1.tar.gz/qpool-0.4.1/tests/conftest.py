# File: tests/conftest.py
"""
Pytest wiring for better wombat diagnostics:
- Force DEBUG-level logs to a temp file via env vars.
- On any test failure, print the last N lines of the wombat log so retry traces are visible.

Environment variables honored by src/wombat/multiprocessing/log.py:
  WOMBAT_LOG_FILE, WOMBAT_LOG_LEVEL, WOMBAT_LOG_STDOUT, WOMBAT_LOG_MAX, WOMBAT_LOG_BACKUPS
"""

import io
import logging
import multiprocessing
import os
import sys
import tempfile
import time

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

WOMBAT_LOG_PATH_FOR_TESTS: str | None = None


@pytest.fixture(autouse=True, scope="session")
def _wombat_debug_logging_session():
    """
    Session-scoped fixture that configures a temporary log file for wombat tests.
    The file is preserved after the session for postmortem.
    """
    global WOMBAT_LOG_PATH_FOR_TESTS
    tmpdir = tempfile.mkdtemp(prefix="wombat_logs_")
    log_path = os.path.join(tmpdir, "wombat.log")
    WOMBAT_LOG_PATH_FOR_TESTS = log_path
    yield
    # Keep the temp log directory for inspection; do not delete here.


@pytest.fixture
def logging_config():
    """Provides logging config for tests, using the globally set log path."""
    if not WOMBAT_LOG_PATH_FOR_TESTS:
        pytest.fail("WOMBAT_LOG_PATH_FOR_TESTS not set by session fixture.")
    return {
        "log_file": WOMBAT_LOG_PATH_FOR_TESTS,
        "level": logging.DEBUG,
    }


def _tail(path: str, lines: int = 300) -> str:
    """
    Return the last `lines` lines of a file located at `path`.
    Robust for large files via backward reads; falls back to full read on errors.
    """
    try:
        with open(path, "rb") as f:
            try:
                f.seek(0, io.SEEK_END)
                file_size = f.tell()
                if file_size == 0:
                    return "<empty log file>"
                block = 4096
                data = bytearray()
                # Read from the end in blocks until we have enough lines
                while len(data.splitlines()) <= lines and f.tell() > 0:
                    read_size = min(block, f.tell())
                    f.seek(f.tell() - read_size)
                    chunk = f.read(read_size)
                    f.seek(f.tell() - read_size)
                    data[:0] = chunk
                    if f.tell() == 0:
                        break
                text = data.decode(errors="replace")
                return "\n".join(text.splitlines()[-lines:])
            except Exception:
                f.seek(0)
                return f.read().decode(errors="replace")
    except FileNotFoundError:
        return "<wombat log file not found>"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hookwrapper implementation:
    - Let pytest run the phase.
    - If the call phase failed, print the tail of the wombat log.
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        path = WOMBAT_LOG_PATH_FOR_TESTS or "logfile.log"
        tail = _tail(path, lines=300)
        # Use a clear delimiter so it's easy to grep in CI logs.
        print("\n================= WOMBAT LOG TAIL (last 300 lines) =================")
        print(tail)
        print("================= END WOMBAT LOG TAIL =================\n")


@pytest.fixture(autouse=True)
def _process_cleanup_checker():
    """
    Fixture to ensure no child processes are left running after a test.
    This prevents hangs at the end of the test suite by failing the offending test.
    """
    yield  # Run the test

    # Teardown check: Give processes a moment for graceful shutdown.
    time.sleep(1)
    lingering_processes = multiprocessing.active_children()

    if lingering_processes:
        process_names = [p.name for p in lingering_processes]
        pytest.fail(
            f"Test left lingering child processes: {process_names}. "
            "This will cause the test suite to hang."
        )
