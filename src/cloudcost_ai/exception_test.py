from cloudcost_ai.utils.exception import CustomException

try:
    result = 10 / 0
except Exception as error:
    raise CustomException(error) from error