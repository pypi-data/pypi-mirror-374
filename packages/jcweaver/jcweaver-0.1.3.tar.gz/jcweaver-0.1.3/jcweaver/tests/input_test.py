from jcweaver.api.api import input_prepare
from jcweaver.api.decorators import lifecycle
from jcweaver.core.const import DataType, Platform


@lifecycle(platform=Platform.MODELARTS)
def my_input():
    dataset = input_prepare(DataType.DATASET, "")
    print("file path: ", dataset.path)
    input2()


def input2():
    dataset = input_prepare(DataType.DATASET, "")
    print("file path2: ", dataset.path)


def test_input():
    my_input()

