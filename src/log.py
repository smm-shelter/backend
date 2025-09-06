import logging
from src.settings import settings

logger = logging.getLogger("_granian")
if settings.MODE == "debug":
    logger.setLevel(logging.DEBUG)
