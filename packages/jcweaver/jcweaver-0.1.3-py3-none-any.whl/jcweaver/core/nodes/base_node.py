from __future__ import annotations

import atexit
import os
from typing import Any, Dict, Generic, TypeVar, List

import requests

# 作用是 在类型注解中引入泛型（generic types），让函数、类能支持多种类型，而不仅仅是写死的某个类型。
TInputs = TypeVar("TInputs")
TOutputs = TypeVar("TOutputs")


class OutputRef:
    def __init__(self, node: "Node", key: str):
        self.node = node
        self.key = key

    def resolve(self) -> Dict[str, str]:
        return {"node_id": self.node.id, "output_key": self.key}

    def __repr__(self):
        return f"<LazyOutputRef {self.node.name}.{self.key}>"


# 通过 Generic[T] 告诉类型检查器：这个类依赖于一个类型参数 T，Generic[T] 的主要作用是 声明类的类型参数
# TypeVar 定义类型变量。 Generic 让类声明自己支持哪些类型变量。 两者配合，才能写出泛型类，就像 list[T]、dict[K, V] 一样。
class Node(Generic[TInputs, TOutputs]):
    id_counter = 0

    def __init__(self, name: str, node_type, description: str):
        Node.id_counter += 1
        self.id = str(Node.id_counter)
        self.node_type = node_type
        self.name = name
        self.description = description
        self.dependencies: list[str] = []
        self.params: Dict[str, Any] = {}
        self.inputs: TInputs = None  # 子类会填
        self.outputs: TOutputs = None  # 子类会填
        # 自动注册到 workflow
        workflow.add_node(self)

    def set_param(self, key: str, value: Any):
        # 类型检查
        if not hasattr(self.inputs, key):
            raise AttributeError(f"Invalid param '{key}' for {self.__class__.__name__}")
        # expected_type = next(f.type for f in fields(self.inputs) if f.name == key)
        # if not isinstance(value, expected_type) and not isinstance(value, LazyOutputRef):
        #     raise TypeError(f"Param '{key}' expects {expected_type}, got {type(value)}")

        self.params[key] = value
        if isinstance(value, OutputRef):
            self.dependencies.append(value.node.id)
        return self

    def output(self, key: str) -> OutputRef:
        if not hasattr(self.outputs, key):
            raise AttributeError(f"Invalid output '{key}' for {self.__class__.__name__}")
        return OutputRef(self, key)

    def to_dict(self) -> Dict[str, Any]:
        def serialize(value: Any):
            if isinstance(value, OutputRef):
                return value.resolve()
            return value

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
            "depends_on": self.dependencies,
            "params": {k: serialize(v) for k, v in self.params.items()},
        }


class Workflow:
    def __init__(self, filename="workflow.json"):
        self.nodes: List["Node"] = []
        self.filename = filename
        # 注册退出钩子
        atexit.register(self._save_on_exit)

    def add_node(self, node: "Node"):
        self.nodes.append(node)

    def to_dict(self) -> Dict[str, Any]:
        return {"workflow": [node.to_dict() for node in self.nodes]}

    # def _save_on_exit(self):
    #     with open(self.filename, "w", encoding="utf-8") as f:
    #         json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    #     print(f"[JCWeaver] workflow saved to {self.filename}")

    def _save_on_exit(self):
        url = os.getenv("url", "").strip()
        data = self.to_dict()

        if not url:
            # url 为空，不做任何事
            print(f"[JCWeaver] the code executed successfully")
            return

        try:
            headers = {"Content-Type": "application/json"}
            resp = requests.post(url, json=data, headers=headers, timeout=10)
            resp.raise_for_status()
            print(f"[JCWeaver] workflow posted to {url}, status={resp.status_code}")
        except Exception as e:
            print(f"[JCWeaver] failed to post workflow: {e}")


# 全局 workflow 实例
workflow = Workflow()
