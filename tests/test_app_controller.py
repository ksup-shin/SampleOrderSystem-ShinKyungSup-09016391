import pytest

from mvc import View
from sample_order_system.app.model import SampleOrderModel
from sample_order_system.app.controller import SampleOrderController


class FakeView(View):
    def __init__(self):
        self.renders = []
        self.errors = []
        self.messages = []

    def render(self, state):
        self.renders.append(state.screen)

    def show_error(self, message):
        self.errors.append(message)

    def show_message(self, message):
        self.messages.append(message)


@pytest.fixture
def files(tmp_path):
    return {
        "samples_file": tmp_path / "samples.json",
        "orders_file": tmp_path / "orders.json",
        "queue_file": tmp_path / "queue.json",
    }


@pytest.fixture
def controller(files):
    model = SampleOrderModel(**files)
    view = FakeView()
    return SampleOrderController(model, view)


def test_dispatch_main_menu_1_enters_sample_menu(controller):
    controller.dispatch("1")

    assert controller.model.screen == "samples"


def test_dispatch_0_from_submenu_returns_to_main_menu(controller):
    controller.dispatch("1")

    controller.dispatch("0")

    assert controller.model.screen == "main"


def test_dispatch_unknown_command_shows_error_without_crashing(controller):
    result = controller.dispatch("nonexistent")

    assert result is True
    assert controller.view.errors


def test_dispatch_exit_command_returns_false(controller):
    result = controller.dispatch("0")

    assert result is False
