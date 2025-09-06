import logging
from src.settings import settings

if settings.MODE == "debug":
    logger = logging.getLogger("granian.access")
else:
    logger = logging.getLogger("_granian")
