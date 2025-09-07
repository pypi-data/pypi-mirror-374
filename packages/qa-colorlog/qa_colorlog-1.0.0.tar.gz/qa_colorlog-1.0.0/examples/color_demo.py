from logger import logger, LogColor


def main():
    logger.info("Testing different log levels")

    logger.debug("Debug level - light grey")
    logger.info("Info level - green")
    logger.warning("Warning level - yellow")
    logger.error("Error level - red")
    logger.critical("Critical level - magenta")

    print(f"Available colors: {[color.name for color in LogColor]}")


if __name__ == "__main__":
    main()
