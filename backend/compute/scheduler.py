from .device import Device
from . import cpu, gpu


class Scheduler:

    def run(self, task):

        if task.device == Device.GPU:
            return gpu.submit(task)

        return cpu.submit(task)