from logger import QALogger


def main():
    custom_logger = QALogger("my_app")

    custom_logger.info("Custom logger instance")
    custom_logger.debug("Debug from custom logger")
    custom_logger.error("Error from custom logger")


if __name__ == "__main__":
    main()
