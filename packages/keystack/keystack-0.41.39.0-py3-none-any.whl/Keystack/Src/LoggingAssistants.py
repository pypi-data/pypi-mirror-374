""" 
Logs for test session main loggings.
Not test case logs.
"""

import logging
import inspect
import sys
from pydantic import Field, dataclasses


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
        
@dataclasses.dataclass
class TestSessionLoggerAssistant:
    testSessionLogFile: str
    enableStdoutStreaming: bool = False
    
    def __post_init__(self):
        self.logger = None
        dateTimeFormat = '%m-%d-%Y %H:%M:%S'
                
        logging.basicConfig(
            level=logging.DEBUG,
            filename=self.testSessionLogFile,
            format="%(levelname)s: %(asctime)s:%(msecs)03d: %(message)s",
            datefmt=dateTimeFormat
        )
        
        self.logger = logging.getLogger()

        # Silence all module loggings!
        for log_name, log_obj in logging.Logger.manager.loggerDict.items():
            if log_name != __name__:
                log_obj.disabled = True
        
        # Stream to stdout
        if self.enableStdoutStreaming:
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
        
    def getCallInfo(self, message, stdout=False):
        """
        __get_cal_info: /opt/Keystack/Src/keystack.py __post_init__ 138
        """
        stack = inspect.stack()

        # stack[1] gives previous function ('info' in our case)
        # stack[2] gives before previous function and so on
        # Example: DEBUG: 05-27-2025 08:24:59:052: /opt/keystack_src/Src/RunTaskAssistants/RunTask.py -> run() -> 791: TaskName: bringup   skipTask=False
        fileName = stack[2][1]
        lineNumber = stack[2][2]
        functionName = stack[2][3]
        
        if stdout:
            print(f'{message}\n')
            
        return f'{fileName} -> {functionName}() -> {lineNumber}: {message}\n'
    
    def info(self, message: str='', stdout: bool=False):
        self.logger.info(self.getCallInfo(message, stdout))
        
    def warning(self, message: str='', stdout: bool=False):
        self.logger.warning(self.getCallInfo(message, stdout))
        
    def debug(self, message: str='', stdout: bool=False):
        self.logger.debug(self.getCallInfo(message, stdout))
        
    def error(self, message: str='', stdout: bool=False):
        self.logger.error(self.getCallInfo(message, stdout))
    
    def failed(self, message: str='', stdout: bool=False):
        self.logger.fatal(self.getCallInfo(message, stdout))
        
