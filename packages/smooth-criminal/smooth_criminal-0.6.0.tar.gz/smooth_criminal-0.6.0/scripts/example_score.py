import logging
import os

from rich.logging import RichHandler

from smooth_criminal.core import auto_boost


log_level = os.getenv("LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, log_level, logging.INFO)

logging.basicConfig(
    level=numeric_level,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
    force=True,
)

logger = logging.getLogger("SmoothCriminal")

@auto_boost()
def calculate_stuff():
    return sum(range(500_000))

if __name__ == "__main__":
    logger.info("Running calculate_stuff() to record its performance...")
    result = calculate_stuff()
    logger.info(f"Result: {result}")
