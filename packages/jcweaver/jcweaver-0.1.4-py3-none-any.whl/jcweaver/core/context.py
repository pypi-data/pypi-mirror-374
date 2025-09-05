import argparse
import os
import time
import uuid

_forced_platform = None

parser = argparse.ArgumentParser(description='env')
parser.add_argument("--CURRENT_PLATFORM", help="platform name", default="None")
args, unknown = parser.parse_known_args()


def default_context():
    return {
        "trace_id": str(uuid.uuid4()),
        "timestamp": int(time.time()),
        "logger": None  # 可注入 get_logger("task-name")
    }


def set_forced_platform(name: str):
    global _forced_platform
    _forced_platform = name


def get_platform():
    if _forced_platform:
        return _forced_platform
    if args.CURRENT_PLATFORM != "None":
        return args.CURRENT_PLATFORM
    return _forced_platform or os.environ.get("CURRENT_PLATFORM", "local") or args.platform
