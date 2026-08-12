from .scheduler import Scheduler
from .task import ComputeTask


class ComputeExecutor:

    def __init__(self):
        self.scheduler = Scheduler()

    def execute(self, task: ComputeTask):
        return self.scheduler.run(task)