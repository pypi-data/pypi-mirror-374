from logger import QALogger


def main():
    api_logger = QALogger(
        name="api_monitor",
        log_level="INFO",
        log_to_file=True,
        log_file_path="api_logs.log",
        colorize_output=True
    )
    
    api_logger.info("API monitoring started")
    
    endpoints = [
        "/api/users",
        "/api/products", 
        "/api/orders"
    ]
    
    for endpoint in endpoints:
        api_logger.debug(f"Preparing request to {endpoint}")
        api_logger.info(f"Calling {endpoint}")
        
        if endpoint == "/api/orders":
            api_logger.warning(f"Slow response from {endpoint} (>500ms)")
        else:
            api_logger.info(f"Success: {endpoint} responded in 150ms")
    
    api_logger.critical("API monitoring session completed")


if __name__ == "__main__":
    main()
