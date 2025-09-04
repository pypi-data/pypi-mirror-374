import logging
import os
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logging.Logger.Error = logging.Logger.error


def install_packages():
    packages = [
        "jcweaver==0.1.1",
    ]
    for pkg in packages:
        logger.info(f"正在安装 {pkg} ...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", pkg,
            "-i", "https://mirrors.aliyun.com/pypi/simple/"
        ])


try:
    from jcweaver.api import input_prepare, output_prepare, lifecycle
    from jcweaver.core.const import DataType
except ImportError:
    install_packages()
    from jcweaver.api import input_prepare, output_prepare, lifecycle
    from jcweaver.core.const import DataType

input_file_path = input_prepare(DataType.DATASET, '')
output_file_path = output_prepare(DataType.DATASET, 'output.txt')


@lifecycle()
def run():
    paths = os.listdir(input_file_path)
    print("输入文件路径:", input_file_path)
    print(paths)

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write("dataset path: ")
        f.write(str(paths))


if __name__ == '__main__':
    run()
