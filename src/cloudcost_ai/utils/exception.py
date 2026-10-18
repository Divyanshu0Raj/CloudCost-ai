import sys

from cloudcost_ai.utils.logger import get_logger

logger=get_logger(__name__)

def error_message_detail(error):

    _,_,exc_tb=sys.exc_info()

    if exc_tb is None:
        return str(error)

    file_name=exc_tb.tb_frame.f_code.co_filename
    line_number=exc_tb.tb_lineno

    return (
        f"File: {file_name}|"
        f"Line: {line_number}|"
        f"Error: {error}"
    )

class CustomException(Exception):

    def __init__(self,error):

        self.error_message=error_message_detail(error)
        super().__init__(self.error_message)
        logger.error(self.error_message)

    def __str__(self):
        return self.error_message