from __future__ import annotations
from typing import Callable, Dict, List, Any, DefaultDict
from collections import defaultdict

class EventBus:
    def __init__(self):
        self._subs: DefaultDict[str, List[Callable[[Dict[str, Any]], None]]] = defaultdict(list)

    def subscribe(self, topic: str, fn: Callable[[Dict[str, Any]], None]) -> None:
        self._subs[topic].append(fn)

    def publish(self, topic: str, msg: Dict[str, Any]) -> None:
        for fn in self._subs.get(topic, []):
            fn(msg)
