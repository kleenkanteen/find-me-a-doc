from inspect import currentframe, getframeinfo
import inspect

def get_linenumber():
    cf = currentframe()
    line_number = cf.f_back.f_lineno
    return line_number

def get_filename():
   cf = currentframe()
   filename = getframeinfo(cf).filename
   return filename

def get_function_name():
    caller_name = inspect.stack()[3].function
    return caller_name