import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

PROJECT_ROOT=Path(__file__).resolve().parents[3]
LOGS_DIR=PROJECT_ROOT/"logs"
LOGS_DIR.mkdir(parents=True,exist_ok=True)

LOG_FILE_PATH=LOGS_DIR/"application.log"

LOG_FORMAT="[%(asctime)s] %(levelname)s - %(message)s"

FORMATTER=logging.Formatter(LOG_FORMAT)

def get_logger(name: str= "cloudcost_ai")-> logging.Logger:

    logger=logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate=False

    if logger.handlers:
        return logger
    
    file_handler=TimedRotatingFileHandler(
        filename=LOG_FILE_PATH,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(FORMATTER)

    console_handler=logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(FORMATTER)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

print("Logger initialized. Logs will be saved to:", LOG_FILE_PATH)
if __name__=="__main__":
    logger=get_logger("cloudecost_ai.logger")
    logger.info("Application started")
    logger.warning("this is a waarning ")
    logger.error("this is an error ")