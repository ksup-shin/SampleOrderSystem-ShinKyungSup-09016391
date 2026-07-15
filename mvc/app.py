"""Application: wires a Model/View/Controller triple together and runs the CUI loop."""

from __future__ import annotations

from .controller import Controller
from .model import Model
from .view import View


class Application:
    """
    Owns one Model/View/Controller triple and drives the console read-eval loop.

    Usage as a library from another program:

        from mvc import Application
        from my_app import MyModel, MyView, MyController

        app = Application(MyModel(), MyView(), MyController)
        app.run()

    `controller_factory` receives (model, view) and must return a Controller.
    Passing an already-constructed Controller is also supported.
    """

    def __init__(
        self,
        model: Model,
        view: View,
        controller: Controller | type[Controller],
        prompt: str = "> ",
    ) -> None:
        self.model = model
        self.view = view
        self.controller = (
            controller(model, view) if isinstance(controller, type) else controller
        )
        self.prompt = prompt
        self._running = False

    def run(self) -> None:
        """Start the read-eval-render loop. Blocks until a command returns False."""
        self._running = True
        self.view.render(self.model)
        while self._running:
            try:
                raw = self.view.input(self.prompt).strip()
            except (EOFError, KeyboardInterrupt):
                self.view.print()
                break

            if not raw:
                continue

            command, *args = raw.split()
            try:
                self._running = self.controller.dispatch(command, *args)
            except Exception as exc:  # noqa: BLE001 - surface any handler error to the console
                self.view.show_error(str(exc))

    def stop(self) -> None:
        """Allow a controller/model to request the loop stop externally."""
        self._running = False
