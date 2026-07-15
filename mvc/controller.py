"""Base Controller: translates user input (via View) into Model mutations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .model import Model
from .view import View


class Controller(ABC):
    """
    Base class for all controllers.

    A controller owns a reference to one Model and one View. It:
      - registers itself as a Model observer so it can push updates to the View
      - exposes `dispatch(command, *args)` so a View/Application can route
        raw user commands into model-mutating handlers.
    """

    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.model.add_observer(self.on_model_changed)

    def on_model_changed(self, model: Model, event: str, data) -> None:
        """Default reaction to any model change: re-render the view."""
        self.view.render(model)

    @abstractmethod
    def dispatch(self, command: str, *args: str) -> bool:
        """
        Handle a single user command.

        Return True to keep the application loop running, False to signal
        that the application should stop (e.g. on an "exit"/"quit" command).
        """
        raise NotImplementedError
