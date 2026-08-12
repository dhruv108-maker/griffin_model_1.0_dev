from enum import Enum

class Device(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    AUTO = "auto"