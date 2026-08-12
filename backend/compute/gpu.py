def submit(task):
    return task.fn(
        *task.args,
        **task.kwargs
    )