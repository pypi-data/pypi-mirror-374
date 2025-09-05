import json
import os

from jcweaver.adapter.BaseAdapter import BaseAdapter
from jcweaver.core.logger import logger
from jcweaver.core.const import DataType


class OctopusAdapter(BaseAdapter):
    def __init__(self):
        from c2net.context import prepare, upload_output
        self._prepare = prepare()
        self._upload_output = upload_output
        self.output = ""

    def before_task(self, inputs, context: dict):
        logger.info("execute before task")
        pass

    def after_task(self, outputs, context: dict):
        logger.info("execute after task")
        self._upload_output()

    def input_prepare(self, data_type: str, file_path: str):
        if data_type == DataType.DATASET:
            ds_url = os.environ.get("DATASET_URL")
            data = json.loads(ds_url)
            # 提取 dataset_name != "dataset" 的值，并去掉后缀
            for item in data:
                name = item["dataset_name"]
                if name != "dataset":
                    # 去掉文件后缀
                    name_no_ext, _ = os.path.splitext(name)
                    return os.path.join(self._prepare.dataset_path, name_no_ext)

            logger.error("No dataset found")
            return self._prepare.dataset_path

        if data_type == DataType.MODEL:
            return os.path.join(self._prepare.pretrain_model_path, file_path)
        if data_type == DataType.CODE:
            return os.path.join(self._prepare.code_path, file_path)
        logger.error(f"Unknown data type for input: {data_type}")
        return ""

    def output_prepare(self, data_type: str, file_path: str):
        self.output = os.path.join(self._prepare.output_path, file_path)
        return self.output
