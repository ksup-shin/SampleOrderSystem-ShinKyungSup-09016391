"""Base Model: holds application state and notifies observers when it changes."""

from __future__ import annotations

from typing import Any, Callable

Observer = Callable[["Model", str, Any], None]


class Model:
    """
    Base class for all models.

    A model owns state only. It must never import or reference a View or Controller.
    Subclasses call `self.notify(event, data)` whenever state changes that a
    Controller/View should react to (e.g. after a mutation).
    """

    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def add_observer(self, observer: Observer) -> None:
        """Register a callback: observer(model, event: str, data: Any) -> None."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: str, data: Any = None) -> None:
        """Notify all observers that `event` occurred, carrying optional `data`."""
        for observer in list(self._observers):
            observer(self, event, data)
