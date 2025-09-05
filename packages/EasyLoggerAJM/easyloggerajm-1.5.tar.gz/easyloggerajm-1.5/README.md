# EasyLoggerAJM

## Description
EasyLoggerAJM is a comprehensive logging utility designed to provide an easy-to-use interface for logging messages in various formats and levels. It comes with advanced features such as custom log formats, timestamping, and streamlined console logging.

## Classes and Methods

### ConsoleOneTimeFilter
This class provides a filter to ensure that each message is logged only once to the console.

#### Attributes:
- `logged_messages`: Stores messages that have been logged to prevent duplicate logging.

#### Methods:
- `__init__`: Initializes the filter.
- `filter`: Filters messages to ensure they are not logged more than once.

### _EasyLoggerCustomLogger
This internal class includes various methods to log messages at different levels.

#### Methods:
- `_print_msg`: Internal method to print the log message.
- `info`: Logs an informational message.
- `warning`: Logs a warning message.
- `error`: Logs an error message.
- `debug`: Logs a debug message.
- `critical`: Logs a critical message.

### EasyLogger
The main class providing extensive logging functionality.

#### Class Attributes:
- `DEFAULT_FORMAT`: Default format for log messages.
- `INT_TO_STR_LOGGER_LEVELS`: Mapping of integer to string log levels.
- `STR_TO_INT_LOGGER_LEVELS`: Mapping of string to integer log levels.
- `MINUTE_LOG_SPEC_FORMAT`: Log specification format for minute-level logging.
- `MINUTE_TIMESTAMP`: Format for minute-level timestamp.
- `HOUR_LOG_SPEC_FORMAT`: Log specification format for hour-level logging.
- `HOUR_TIMESTAMP`: Format for hour-level timestamp.
- `DAILY_LOG_SPEC_FORMAT`: Log specification format for daily-level logging.
- `DAILY_TIMESTAMP`: Format for daily-level timestamp.
- `LOG_SPECS`: Log specification details.

#### Instance Attributes:
- `formatter`: Formatter used for log messages.
- `_log_location`: Location for log files.
- `logger`: Main logger instance.
- `_inner_log_fstructure`: Inner log file structure.
- `show_warning_logs_in_console`: Flag to show warning logs in the console.
- `_root_log_location`: Root location for logs.
- `_project_name`: Project name for which log is being created.
- `_log_spec`: Specification for log format.
- `_file_logger_levels`: File logger levels.
- `timestamp`: Timestamp format used for logging.

#### Methods:
- `__init__`: Initializes the EasyLogger.
- `UseLogger`: Set up the logger.
- `file_logger_levels`: Set file logger levels.
- `project_name`: Set the project name.
- `inner_log_fstructure`: Set the inner log file structure.
- `log_location`: Set the log file location.
- `log_spec`: Set the log specification.
- `set_timestamp`: Set the timestamp format.
- `make_file_handlers`: Create file handlers for logging.
- `create_stream_handler`: Create a stream handler for logging to the console.

## Installation

To set up the project:

1. Clone the repository:
    ```bash
    git clone <repository_url>
    ```
2. Navigate to the project directory:
    ```bash
    cd <project_directory>
    ```
3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To use EasyLogger in your project:
```python
from EasyLoggerAJM import EasyLogger

# Initialize the logger
easy_logger = EasyLogger(project_name="MyProject")

# Set up the logger
logger = easy_logger.logger

# Log messages
logger.info("This is an informational message")
logger.warning("This is a warning message")
logger.error("This is an error message")
```

## Features
- Customizable logging formats and levels
- Streamlined console logging
- Advanced timestamping options

## Contributing

1. Fork the project
2. Create your feature branch:
    ```bash
    git checkout -b feature/YourFeature
    ```
3. Commit your changes:
    ```bash
    git commit -m 'Add some feature'
    ```
4. Push to the branch:
    ```bash
    git push origin feature/YourFeature
    ```
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.

## Authors

- amcsparron2793-Water - [Your GitHub Profile](https://github.com/amcsparron2793-Water)

## Acknowledgments

- Special thanks to anyone whose code, libraries, or tutorials were used to help create this project.