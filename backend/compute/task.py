from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class ComputeTask:
    name: str
    fn: Callable
    args: tuple = ()
    kwargs: dict = None
    device: str = "auto"

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}