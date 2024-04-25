from inspect import currentframe, getframeinfo
import inspect

def get_linenumber():
    line_number = inspect.stack()[3].lineno
    return line_number

def get_filename():
    filename = inspect.stack()[3].filename
    return filename

def get_function_name():
    caller_name = inspect.stack()[3].function
    return caller_name