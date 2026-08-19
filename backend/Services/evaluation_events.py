import queue
import threading
from collections import defaultdict
from typing import Any


class EvaluationEventBus:
    """In-process fan-out bus for live evaluation progress events."""

    _lock = threading.Lock()
    _subscribers: dict[str, set[queue.Queue]] = defaultdict(set)

    @classmethod
    def subscribe(cls, evaluation_id: str) -> queue.Queue:
        channel: queue.Queue = queue.Queue()
        with cls._lock:
            cls._subscribers[evaluation_id].add(channel)
        return channel

    @classmethod
    def unsubscribe(cls, evaluation_id: str, channel: queue.Queue) -> None:
        with cls._lock:
            subscribers = cls._subscribers.get(evaluation_id)
            if not subscribers:
                return
            subscribers.discard(channel)
            if not subscribers:
                cls._subscribers.pop(evaluation_id, None)

    @classmethod
    def publish(cls, evaluation_id: str, event: dict[str, Any]) -> None:
        with cls._lock:
            subscribers = tuple(cls._subscribers.get(evaluation_id, ()))

        for channel in subscribers:
            try:
                channel.put_nowait(event)
            except queue.Full:
                # Progress is best-effort; the next event supersedes stale UI state.
                pass
