import logging
import re
import sys


def setup_logging(debug: bool = False) -> None:
    """Configure structured JSON-style logging for the application."""
    level = logging.DEBUG if debug else logging.INFO
    fmt = (
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"logger": "%(name)s", "message": %(message)s}'
    )
    logging.basicConfig(
        level=level,
        format=fmt,
        stream=sys.stdout,
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def mask_cpf(cpf: str) -> str:
    """Return CPF with middle digits masked for PII-safe logging."""
    digits = re.sub(r"\D", "", cpf)
    if len(digits) == 11:
        return f"***.***.***-{digits[9:]}"
    return "***MASKED***"
