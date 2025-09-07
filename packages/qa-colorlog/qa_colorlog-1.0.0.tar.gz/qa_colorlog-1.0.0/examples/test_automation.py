import os
from logger import QALogger


def main():
    os.environ['LOGGER_LOG_LEVEL'] = 'INFO'
    os.environ['LOGGER_LOG_TO_FILE'] = 'true'
    os.environ['LOGGER_LOG_FILE_PATH'] = 'test_results.log'
    os.environ['LOGGER_COLORIZE_OUTPUT'] = 'true'
    
    test_logger = QALogger("test_runner")
    
    test_logger.info("Starting test suite execution")
    
    test_cases = ["test_login", "test_search", "test_checkout"]
    
    for i, test_case in enumerate(test_cases, 1):
        test_logger.debug(f"Preparing test case: {test_case}")
        test_logger.info(f"Executing test {i}/{len(test_cases)}: {test_case}")
        
        if test_case == "test_search":
            test_logger.warning("Search functionality is slow, investigating...")
        elif test_case == "test_checkout":
            test_logger.error("Payment gateway timeout detected")
        else:
            test_logger.info(f"Test {test_case} passed successfully")
    
    test_logger.critical("Test suite completed with errors")


if __name__ == "__main__":
    main()
