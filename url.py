import pandas as pd
from typing import Union, List, Optional
import logging
from io import BytesIO
import os
from urllib.parse import urlparse
import requests
from pathlib import Path
# from logging import handlers
from logger_experiment import logger_experiment

logger = logger_experiment(name="lilly_auth")

def check_remote_file(url):
    """Check if a remote file exists via HTTP/HTTPS."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Remote file check failed for Check_remote_file function {url}: {e}")
        return False


def _strip_outer_quotes(s: str) -> str:
    """Remove a single pair of leading/trailing quotes if present."""
    if len(s) >= 2 and ((s[0] == s[-1]) and s[0] in ("'", '"')):
        return s[1:-1]
    return s

def _file_url_to_path(file_url: str) -> Path:
    """
    Convert file:// URL to a platform-correct Path.
    Handles Windows drive letters and UNC paths.
    Examples:
      - file:///C:/Users/name/file.xlsx
      - file://server/share/file.xlsx  (UNC)
      - file:///home/name/file.xlsx    (POSIX)
    """
    parsed = urlparse(file_url)
    if parsed.scheme.lower() != "file":
        raise ValueError(f"Not a file:// URL: {file_url}")

    # Netloc is used for UNC on Windows: file://server/share/dir/file.xlsx
    netloc = parsed.netloc
    path = unquote(parsed.path or "")

    if os.name == "nt":
        # UNC: file://server/share/path -> \\server\share\path
        if netloc:
            unc = f"\\\\{netloc}{path.replace('/', '\\')}"
            return Path(unc)

        # Drive letter: parsed.path may be like /C:/dir/file.xlsx
        if path.startswith("/") and len(path) >= 3 and path[2] == ":":
            path = path.lstrip("/")  # -> C:/dir/file.xlsx

        return Path(path)
    else:
        # POSIX: netloc is typically empty; path is absolute
        return Path(path)

def check_remote_file(url: str) -> bool:
    """
    Lightweight URL sanity check without network I/O.
    (If you want real checking, replace with requests.head(url, timeout=5).)
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False

def url_input(
    url: Optional[Union[str, os.PathLike, BytesIO, object]] = None
) -> Union[str, Path, BytesIO, object]:
    """
    Validate and return a URL or local file path for Excel input.
    - Accepts: str (local path or URL), PathLike, file-like (has .read), bytes (wrapped to BytesIO).
    - Prompts if no value provided.
    - Cross-platform normalization (Windows/macOS/Linux).
    Returns:
      - For local paths: absolute Path (resolved)
      - For file:// URLs: resolved Path
      - For http(s): URL string
      - For file-like: the object as-is
      - For bytes: BytesIO
    """
    try:
        # Prompt only if url not provided
        if not url:
            raw = input("Enter the path or URL of the Excel file: ").strip()
        else:
            raw = url

        # File-like objects (must have read method)
        if hasattr(raw, "read"):
            logger.info("File-like object provided.")
            return raw

        # Bytes → BytesIO
        if isinstance(raw, bytes):
            logger.warning("Byte string received; wrapping in BytesIO.")
            return BytesIO(raw)

        # PathLike → str
        if isinstance(raw, os.PathLike):
            raw = str(raw)

        if isinstance(raw, str):
            s = _strip_outer_quotes(raw.strip())

            # Handle file:// URLs (cross-platform)
            if s.lower().startswith("file://"):
                p = _file_url_to_path(s).expanduser()
                if p.exists():
                    logger.info(f"Valid file:// path: {p}")
                    return p.resolve()
                else:
                    raise FileNotFoundError(f"File not found at {p}")

            # Handle http(s) URLs
            if s.lower().startswith(("http://", "https://")):
                if check_remote_file(s):
                    logger.info(f"Valid remote URL: {s}")
                    return s
                raise FileNotFoundError(f"Remote URL looks invalid or unreachable: {s}")

            # Treat as local path (normalize with pathlib)
            p = Path(s).expanduser()

            # Windows-specific normalization for pasted forward slashes
            if os.name == "nt":
                # Convert forward slashes to backslashes; pathlib already handles many cases,
                # but this helps for pasted strings like C:/Users/... from browsers/Colab.
                p = Path(str(p).replace("/", "\\"))

            # Resolve absolute path and verify existence
            if p.exists():
                logger.info(f"Valid local path: {p}")
                return p.resolve()

            # Final attempt with os.path.normpath (handles odd separator cases)
            norm = os.path.normpath(s)
            if os.path.exists(norm):
                logger.info(f"Valid local path (normalized): {norm}")
                return Path(norm).resolve()

            raise ValueError(f"Invalid path or URL: {s}")

        raise ValueError(f"Unsupported input type: {type(raw)}")

    except Exception as e:
        logger.error(f"Error in url_input: {e}")
        raise
