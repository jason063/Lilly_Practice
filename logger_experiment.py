from logging import handlers
import logging
import os
from pathlib import Path
from typing import Union, List, Optional

LOG_DIR = Path.cwd()  # or Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

def logger_experiment(
    name: str = "lilly_auth",
    log_file: Optional[str] = None,
    level: int = logging.DEBUG,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    rotate_when: str = "midnight",  # 'S','M','H','D','W0'...'W6','midnight'
    backup_count: int = 7
) -> logging.Logger:
    """
    Create and return an idempotent logger with console + timed rotating file handlers.

    - name: logger name (module or app)
    - log_file: file path (defaults to LOG_DIR / 'my_log_file.log')
    - level: base logger level (usually DEBUG)
    - console_level: console verbosity
    - file_level: file verbosity
    - rotate_when: Timed rotation interval
    - backup_count: number of rotated files to keep
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if log_file is None:
        log_file = str(LOG_DIR / "my_log_file.log")

    # Formats
    file_fmt = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(process)d:%(threadName)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_fmt = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    # Helper to prevent duplicate handlers
    def _handler_exists(hcls, level, target=None):
        for h in logger.handlers:
            if isinstance(h, hcls) and h.level == level:
                if isinstance(h, logging.FileHandler):
                    if os.path.abspath(getattr(h, "baseFilename", "")) == os.path.abspath(target or ""):
                        return True
                else:
                    return True
        return False

    # File handler (timed rotation at midnight)
    if not _handler_exists(logging.handlers.TimedRotatingFileHandler, file_level, target=log_file):
        fh = logging.handlers.TimedRotatingFileHandler(
            filename=log_file,
            when=rotate_when,
            interval=1,
            backupCount=backup_count,
            encoding="utf-8",
            utc=False  # set True if you want UTC timestamps
        )
        fh.setLevel(file_level)
        fh.setFormatter(file_fmt)
        logger.addHandler(fh)

    # Console handler
    if not _handler_exists(logging.StreamHandler, console_level):
        ch = logging.StreamHandler()
        ch.setLevel(console_level)
        ch.setFormatter(console_fmt)
        logger.addHandler(ch)

    return logger
