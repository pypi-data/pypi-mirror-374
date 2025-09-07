import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logger import logger


def main():
    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    try:
        _ = 10 / 0
    except ZeroDivisionError:
        logger.exception("Division by zero error")


if __name__ == "__main__":
    main()
