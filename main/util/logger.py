from .source_context import get_filename, get_linenumber, get_function_name

Color = {

    "DEBUG" : '\033[32m', #CYAN
    "WARNING" : '\033[33m', #YELLOW
    "ERROR" : '\033[31m', #RED
    "CRITICAL" : '\033[31m' + '\u001b[1m', #BOLD RED
    "RESET" : '\033[0m',  # Reset to default color
}

class logger_class():

    def __log(self, level: str, message: str):

      global last_function_name

      function_name = get_function_name()
      line_number = get_linenumber()
      filename = get_filename()

      print(Color[level] + f'\nFile "{filename}", line {line_number}, in {function_name}' + Color["RESET"])
      print(Color[level] + f"{level}: {message}" + Color["RESET"])

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
        