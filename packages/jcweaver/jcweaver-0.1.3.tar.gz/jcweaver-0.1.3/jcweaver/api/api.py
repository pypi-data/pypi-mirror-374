from jcweaver.adapter import get_adapter
from jcweaver.core.context import get_platform
from jcweaver.core.logger import logger


def input_prepare(data_type: str, file_path: str):
    platform = get_platform()
    adapter = get_adapter(platform)
    if not adapter:
        logger.error("No adapter found for platform: {}".format(platform))
        raise Exception("No adapter found for platform: {}".format(platform))

    try:
        path = adapter.input_prepare(data_type, file_path)
    except Exception as e:
        logger.error("Error in before_task: {}".format(e))
        raise

    return path


def output_prepare(data_type: str, file_path: str):
    platform = get_platform()
    adapter = get_adapter(platform)
    if not adapter:
        logger.error("No adapter found for platform: {}".format(platform))
        raise Exception("No adapter found for platform: {}".format(platform))

    try:
        path = adapter.output_prepare(data_type, file_path)
    except Exception as e:
        logger.error("Error in before_task: {}".format(e))
        raise

    return path
