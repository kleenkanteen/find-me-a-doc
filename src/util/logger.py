import logging, datetime

from .source_context import get_filename, get_function_name, get_linenumber

formatter = logging.Formatter('%(asctime)s \n%(levelname)s \n%(message)s\n')

class logger_class:

    def __init__(self):
        self.logger = self.__setup_logger('twilio_info', 'twilio_info.log')
        self.twilio_logger = self.__setup_logger('raw_responses', 'raw_responses.log')
        self.completed_call_info_logger = self.__setup_logger('completed_call_info', 'completed_call_info.log')

    def __setup_logger(self, name, log_file, level=logging.INFO):
      """To setup as many loggers as you want"""

      handler = logging.FileHandler(log_file)        
      handler.setFormatter(formatter)

      logger = logging.getLogger(name)
      logger.setLevel(level)
      logger.addHandler(handler)

      return logger

    def __log(self, level: str, message: str):

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

    def loud(self, message: str):
        upper_message = message.upper()
        print(f"\n{upper_message}\n")

    def completed_call_info(self, data: dict, **extra_values):

        # # Array of keys to include in the new dictionary, possible keys: 
        # ['_version', 'sid', 'date_created', 'date_updated', 'parent_call_sid', 'account_sid', 'to', 'to_formatted', '_from', 'from_formatted', 'phone_number_sid', 'status', 'start_time', 'end_time', 'duration', 'price', 'price_unit', 'direction', 'answered_by', 'api_version', 'forwarded_from', 'group_sid', 'caller_name', 'queue_time', 'trunk_sid', 'uri', 'subresource_uris', '_solution', '_context']

        keys_array = [
            "sid",
            "to_formatted",
            "from_formatted",
            "start_time",
            "end_time",
            "account_sid",
            "duration",
            "price",
            "price_unit",
        ]

        call_log_values = {
            **extra_values,
            **{key: data[key] for key in keys_array if key in data},
        }

        log_str = ""
        for key, value in call_log_values.items():
            if isinstance(value, datetime.datetime):
                date_created = value
                value_str = date_created.strftime("%A, %B %d %Y, %H:%M")
            else:
                value_str = str(value)
            log_str += f"{key}: {value_str}\n"

        with open("completed_call_info.log", "a") as f:
            f.write(log_str + "\n")



logger = logger_class()
