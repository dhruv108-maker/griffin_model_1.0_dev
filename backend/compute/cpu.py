from concurrent.futures import ThreadPoolExecutor

_pool = ThreadPoolExecutor(max_workers=8)


def submit(task):
    future = _pool.submit(
        task.fn,
        *task.args,
        **task.kwargs
    )
    return future.result()