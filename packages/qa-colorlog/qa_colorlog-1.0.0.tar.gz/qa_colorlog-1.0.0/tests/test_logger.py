import pytest
import logging
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from logger import QALogger, LogColor, logger
from logger.logger import ColoredFormatter
from logger.config import (
    get_env_bool, get_env_str, get_env_int,
    LOGGER_LOG_LEVEL, LOGGER_LOG_TO_FILE, LOGGER_LOG_FILE_PATH,
    LOGGER_COLORIZE_OUTPUT, LOGGER_DATE_FORMAT, LOGGER_FORMAT
)


class TestLogColor:
    def test_log_color_enum_values(self):
        assert LogColor.RED.value == "\033[0;31m"
        assert LogColor.GREEN.value == "\033[0;32m"
        assert LogColor.YELLOW.value == "\033[0;33m"
        assert LogColor.RESET.value == "\033[0m"
        
    def test_all_colors_are_strings(self):
        for color in LogColor:
            assert isinstance(color.value, str)
            assert color.value.startswith("\033[")


class TestColoredFormatter:
    def test_colored_formatter_initialization(self):
        formatter = ColoredFormatter("%(message)s", colorize=True)
        assert formatter.colorize is True
        
        formatter_no_color = ColoredFormatter("%(message)s", colorize=False)
        assert formatter_no_color.colorize is False
    
    def test_format_with_colors(self):
        formatter = ColoredFormatter("%(levelname)s - %(message)s", colorize=True)
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test message", args=(), exc_info=None
        )
        
        formatted = formatter.format(record)
        assert LogColor.GREEN.value in formatted
        assert LogColor.RESET.value in formatted
        assert "test message" in formatted
    
    def test_format_without_colors(self):
        formatter = ColoredFormatter("%(levelname)s - %(message)s", colorize=False)
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="test message", args=(), exc_info=None
        )
        
        formatted = formatter.format(record)
        assert LogColor.GREEN.value not in formatted
        assert LogColor.RESET.value not in formatted
        assert "INFO - test message" in formatted
    
    def test_level_colors_mapping(self):
        formatter = ColoredFormatter("%(message)s", colorize=True)
        
        test_cases = [
            (logging.DEBUG, LogColor.LIGHT_GREY),
            (logging.INFO, LogColor.GREEN),
            (logging.WARNING, LogColor.YELLOW),
            (logging.ERROR, LogColor.RED),
            (logging.CRITICAL, LogColor.MAGENTA),
        ]
        
        for level, expected_color in test_cases:
            record = logging.LogRecord(
                name="test", level=level, pathname="", lineno=0,
                msg="test", args=(), exc_info=None
            )
            formatted = formatter.format(record)
            assert expected_color.value in formatted


class TestConfigModule:
    def test_get_env_bool_true_values(self):
        with patch.dict(os.environ, {"TEST_BOOL": "true"}):
            assert get_env_bool("TEST_BOOL") is True
        
        with patch.dict(os.environ, {"TEST_BOOL": "1"}):
            assert get_env_bool("TEST_BOOL") is True
            
        with patch.dict(os.environ, {"TEST_BOOL": "yes"}):
            assert get_env_bool("TEST_BOOL") is True
    
    def test_get_env_bool_false_values(self):
        with patch.dict(os.environ, {"TEST_BOOL": "false"}):
            assert get_env_bool("TEST_BOOL") is False
            
        with patch.dict(os.environ, {"TEST_BOOL": "0"}):
            assert get_env_bool("TEST_BOOL") is False
    
    def test_get_env_bool_default(self):
        assert get_env_bool("NONEXISTENT_VAR", True) is True
        assert get_env_bool("NONEXISTENT_VAR", False) is False
    
    def test_get_env_str(self):
        with patch.dict(os.environ, {"TEST_STR": "hello"}):
            assert get_env_str("TEST_STR") == "hello"
        
        assert get_env_str("NONEXISTENT_VAR", "default") == "default"
    
    def test_get_env_int(self):
        with patch.dict(os.environ, {"TEST_INT": "42"}):
            assert get_env_int("TEST_INT") == 42
        
        with patch.dict(os.environ, {"TEST_INT": "invalid"}):
            assert get_env_int("TEST_INT", 100) == 100
        
        assert get_env_int("NONEXISTENT_VAR", 50) == 50


class TestQALogger:
    def test_qa_logger_initialization_defaults(self):
        test_logger = QALogger("test_logger")
        assert test_logger.name == "test_logger"
        assert isinstance(test_logger._logger, logging.Logger)
        assert len(test_logger._logger.handlers) >= 1
    
    def test_qa_logger_initialization_custom_params(self):
        test_logger = QALogger(
            name="custom",
            log_level="ERROR",
            log_to_file=False,
            colorize_output=False
        )
        assert test_logger.name == "custom"
        assert test_logger.level == logging.ERROR
    
    def test_qa_logger_invalid_log_level(self):
        test_logger = QALogger("test", log_level="INVALID")
        assert test_logger.level == logging.DEBUG
    
    def test_qa_logger_set_level_string(self):
        test_logger = QALogger("test")
        test_logger.set_level("ERROR")
        assert test_logger.level == logging.ERROR
    
    def test_qa_logger_set_level_int(self):
        test_logger = QALogger("test")
        test_logger.set_level(logging.WARNING)
        assert test_logger.level == logging.WARNING
    
    def test_qa_logger_logging_methods(self):
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            test_logger = QALogger("test", colorize_output=False)
            
            test_logger.debug("debug message")
            test_logger.info("info message")
            test_logger.warning("warning message")
            test_logger.error("error message")
            test_logger.critical("critical message")
            
            output = fake_stdout.getvalue()
            assert "debug message" in output
            assert "info message" in output
            assert "warning message" in output
            assert "error message" in output
            assert "critical message" in output
    
    def test_qa_logger_exception_logging(self):
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            test_logger = QALogger("test", colorize_output=False)
            
            try:
                raise ValueError("test exception")
            except ValueError:
                test_logger.exception("Exception occurred")
            
            output = fake_stdout.getvalue()
            assert "Exception occurred" in output
            assert "ValueError" in output
    
    def test_qa_logger_file_logging_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            test_logger = QALogger("test", log_to_file=True, log_file_path=str(log_file))
            
            test_logger.info("test file message")
            
            assert log_file.exists()
            content = log_file.read_text()
            assert "test file message" in content
    
    def test_qa_logger_file_logging_failure(self):
        with patch('sys.stdout', new=StringIO()):
            invalid_path = "/invalid/path/test.log"
            test_logger = QALogger("test", log_to_file=True, log_file_path=invalid_path)
            test_logger.info("test message")
    
    def test_qa_logger_file_handler_creates_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "subdir" / "test.log"
            test_logger = QALogger("test", log_to_file=True, log_file_path=str(log_file))
            
            test_logger.info("test message")
            
            assert log_file.parent.exists()
            assert log_file.exists()


class TestDefaultLoggerInstance:
    def test_default_logger_exists(self):
        assert logger is not None
        assert isinstance(logger, QALogger)
    
    def test_default_logger_methods(self):
        assert hasattr(logger, "debug")
        assert hasattr(logger, "info")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "error")
        assert hasattr(logger, "critical")
        assert hasattr(logger, "exception")
    
    def test_default_logger_functionality(self):
        with patch('sys.stdout', new=StringIO()) as fake_stdout:
            temp_logger = QALogger("test_default", colorize_output=False)
            temp_logger.info("test default logger")
            
            output = fake_stdout.getvalue()
            assert "test default logger" in output


class TestEnvironmentIntegration:
    def test_config_uses_environment_variables(self):
        with patch.dict(os.environ, {
            "LOGGER_LOG_LEVEL": "WARNING",
            "LOGGER_LOG_TO_FILE": "true",
            "LOGGER_COLORIZE_OUTPUT": "false"
        }):
            import importlib
            from logger import config
            importlib.reload(config)
            
            assert config.LOGGER_LOG_LEVEL == "WARNING"
            assert config.LOGGER_LOG_TO_FILE is True
            assert config.LOGGER_COLORIZE_OUTPUT is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
