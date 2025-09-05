# File: src/wombat/multiprocessing/log.py
import logging
import os
from logging import Logger
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional, cast

from wombat.utils.errors.decorators import enforce_type_hints_contracts


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def _env_level(name: str, default: int) -> int:
    txt = os.getenv(name)
    if not txt:
        return default
    try:
        # allow "DEBUG", "INFO", or numeric like "10"
        return int(txt)
    except ValueError:
        return getattr(logging, txt.upper(), default)




@enforce_type_hints_contracts
def setup_logging(
    name: str = "WombatLogger",
    level: Optional[int] = None,
    log_file: Optional[str] = None,
    to_console: Optional[bool] = None,
    max_bytes: Optional[int] = None,
    backups: Optional[int] = None,
) -> Logger:
    """
    Create or reuse a logger that writes structured lines.

    Environment overrides (optional):
      WOMBAT_LOG_FILE, WOMBAT_LOG_LEVEL, WOMBAT_LOG_STDOUT, WOMBAT_LOG_MAX, WOMBAT_LOG_BACKUPS
    """
    # Resolve configuration: arguments > environment variables > defaults.
    final_log_file = (
        log_file if log_file is not None else os.getenv("WOMBAT_LOG_FILE", "logfile.log")
    )
    final_level = (
        level
        if level is not None
        else _env_level("WOMBAT_LOG_LEVEL", logging.ERROR)
    )
    final_to_console = (
        to_console
        if to_console is not None
        else _env_bool("WOMBAT_LOG_STDOUT", False)
    )
    final_max_bytes = (
        max_bytes
        if max_bytes is not None
        else _env_int("WOMBAT_LOG_MAX", 2 * 1024 * 1024)
    )
    final_backups = (
        backups if backups is not None else _env_int("WOMBAT_LOG_BACKUPS", 2)
    )

    logger = logging.getLogger(name)
    logger.setLevel(final_level)
    logger.propagate = False  # avoid duplicate lines if root configured elsewhere

    # Basic structured line: timestamp level name pid msg
    fmt = "%(asctime)s | %(levelname)s | %(name)s | pid=%(process)d | %(message)s"
    formatter = logging.Formatter(fmt)

    # Idempotent handler setup
    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        file_handler = RotatingFileHandler(
            final_log_file, mode="a", maxBytes=final_max_bytes, backupCount=final_backups
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(final_level)
        logger.addHandler(file_handler)

    if final_to_console and not any(
        isinstance(h, logging.StreamHandler) for h in logger.handlers
    ):
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(final_level)
        logger.addHandler(sh)

    logger.debug(
        f"Logger initialized: file={final_log_file}, level={logging.getLevelName(final_level)}, console={final_to_console}"
    )
    return logger


def log(worker, message: str, level: int, props: Dict[str, Any]):
    logger: Logger = cast(Logger, props["logger"].instance)
    logger.log(level=level, msg=message)
