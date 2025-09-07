from logger import logger


def main():
    logger.info("This message will be logged to file")
    logger.error("Error message to file")
    logger.warning("Warning message to file")


if __name__ == "__main__":
    main()
