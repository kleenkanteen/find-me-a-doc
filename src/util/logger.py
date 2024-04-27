import logging

from .source_context import get_filename, get_function_name, get_linenumber

Color = {
    "DEBUG": "\033[32m",  # CYAN
    "WARNING": "\033[33m",  # YELLOW
    "ERROR": "\033[31m",  # RED
    "CRITICAL": "\033[31m" + "\u001b[1m",  # BOLD RED
    "RESET": "\033[0m",  # Reset to default color
}

formatter = logging.Formatter('%(asctime)s \n%(levelname)s \n%(message)s\n')

class logger_class:

    def __init__(self):
        self.logger = self.__setup_logger('twilio_info', 'twilio_info.log')
        self.twilio_logger = self.__setup_logger('raw_responses', 'raw_responses.log')

    def __setup_logger(self, name, log_file, level=logging.INFO):
      """To setup as many loggers as you want"""

      handler = logging.FileHandler(log_file)        
      handler.setFormatter(formatter)

      logger = logging.getLogger(name)
      logger.setLevel(level)
      logger.addHandler(handler)

      return logger

    def __log(self, level: str, message: str):

        global last_function_name

        function_name = get_function_name()
        line_number = get_linenumber()
        filename = get_filename()

        print(
            f'{level}: {message} from \n \tFile "{filename}", line {line_number}, in {function_name}'
        )
        self.logger.info(
            f'{message} \n \tfrom File "{filename}", line {line_number}, in {function_name}'
        )

    def twilio_log(self, message: str):
        self.twilio_logger.info(f"{message}")

    def debug(self, message: str):

        self.__log("DEBUG", message)

    def info(self, message: str):

        print(message)

    def warning(self, message: str):

        self.__log("WARNING", message)

    def error(self, message: str):

        self.__log("ERROR", message)

    def critical(self, message: str):

        self.__log("CRITICAL", message)


logger = logger_class()
