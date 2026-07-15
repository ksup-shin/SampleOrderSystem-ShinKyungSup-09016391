"""Base View: renders output to and reads input from a Console (CUI)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class View(ABC):
    """
    Base class for all console (CUI) views.

    A view only knows how to print things and read raw input lines from the
    console. It must never mutate a Model directly and must never contain
    business logic — that belongs in the Controller.
    """

    def print(self, message: str = "") -> None:
        print(message)

    def input(self, prompt: str = "") -> str:
        return input(prompt)

    @abstractmethod
    def render(self, state: Any) -> None:
        """Render the given model state snapshot to the console."""
        raise NotImplementedError

    def show_error(self, message: str) -> None:
        self.print(f"[Error] {message}")

    def show_message(self, message: str) -> None:
        self.print(message)
