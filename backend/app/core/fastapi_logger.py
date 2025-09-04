# 设置日志
from cgitb import handler
import logging
from fastapi.logger import logger as fastapi_logger

gunicorn_error_logger = logging.getLogger("gunicorn.debug")
gunicorn_logger = logging.getLogger("gunicorn")
uvicorn_access_logger = logging.getLogger("unicorn.access")
uvicorn_access_logger.handlers = gunicorn_error_logger.handlers

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)s %(module)s: %(message)s")
)

fastapi_logger.addHandler(handler)
