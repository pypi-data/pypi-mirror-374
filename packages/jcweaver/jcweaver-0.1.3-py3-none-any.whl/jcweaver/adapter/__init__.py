from jcweaver.core.logger import logger
from jcweaver.core.const import PLATFORM_OPENI, PLATFORM_MODELARTS
from .modelarts import ModelArtsAdapter
from .openi import OpenIAdapter


def get_adapter(platform: str):
    platform = platform.lower()
    if platform == PLATFORM_MODELARTS:
        return ModelArtsAdapter()
    elif platform == PLATFORM_OPENI:
        return OpenIAdapter()
    logger.error(f"Unsupported platform: {platform}")
    return None
