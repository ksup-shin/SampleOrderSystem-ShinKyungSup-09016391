import pytest

from mvc import View
from sample_order_system.app.model import SampleOrderModel
from sample_order_system.app.controller import SampleOrderController


class FakeView(View):
    """input()에 미리 정해둔 값을 순서대로 돌려주는 더미 View."""

    def __init__(self, inputs=None):
        self.inputs = list(inputs or [])
        self.prompts = []
        self.renders = []
        self.errors = []
        self.messages = []

    def render(self, state):
        self.renders.append(state.screen)

    def input(self, prompt=""):
        self.prompts.append(prompt)
        return self.inputs.pop(0)

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


def make_controller(files, inputs=None):
    model = SampleOrderModel(**files)
    view = FakeView(inputs=inputs)
    return SampleOrderController(model, view)


def test_dispatch_main_menu_1_enters_sample_menu(files):
    controller = make_controller(files)

    controller.dispatch("1")

    assert controller.model.screen == "samples"


def test_dispatch_0_from_submenu_returns_to_main_menu(files):
    controller = make_controller(files)
    controller.dispatch("1")

    controller.dispatch("0")

    assert controller.model.screen == "main"


def test_dispatch_unknown_command_shows_error_without_crashing(files):
    controller = make_controller(files)

    result = controller.dispatch("nonexistent")

    assert result is True
    assert controller.view.errors


def test_dispatch_exit_command_returns_false(files):
    controller = make_controller(files)

    result = controller.dispatch("0")

    assert result is False


def test_samples_register_prompts_each_field_in_order_and_persists(files):
    controller = make_controller(
        files, inputs=["S-001", "실리콘 웨이퍼-8인치", "0.5", "0.92", "100"],
    )
    controller.model.go_to("samples")

    controller.dispatch("1")

    assert controller.view.prompts == [
        "Sample ID: ", "Name: ", "Avg Production Time: ", "Yield Rate: ", "Initial Stock: ",
    ]
    samples = controller.model.list_samples()
    assert samples == [{
        "id": "S-001", "name": "실리콘 웨이퍼-8인치",
        "avg_production_time": 0.5, "yield_rate": 0.92, "stock": 100,
    }]


def test_reserve_prompts_each_field_and_creates_order(files):
    controller = make_controller(files, inputs=["S-001", "고객", "50", "S-001", "고객B", "10"])
    controller.model.register_sample("S-001", "A", 0.5, 0.9, initial_stock=100)
    controller.model.go_to("reserve")

    controller.dispatch("1")

    assert controller.view.prompts == ["Sample ID: ", "Customer: ", "Quantity: "]
    order = controller.model.list_reserved_orders()[0]
    assert order["sample_id"] == "S-001"
    assert order["customer"] == "고객"
    assert order["quantity"] == 50


def test_approval_approve_lists_reserved_orders_then_prompts_index_and_approves(files):
    controller = make_controller(files, inputs=["2"])
    controller.model.register_sample("S-001", "A", 0.5, 0.9, initial_stock=100)
    order1 = controller.model.reserve_order("S-001", "C1", 10)
    order2 = controller.model.reserve_order("S-001", "C2", 20)
    controller.model.go_to("approval")

    controller.dispatch("2")

    assert controller.view.prompts == ["번호: "]
    assert any(order2["id"] in message for message in controller.view.messages)
    remaining_ids = [o["id"] for o in controller.model.list_reserved_orders()]
    assert order2["id"] not in remaining_ids
    assert order1["id"] in remaining_ids


def test_approval_approve_rejects_out_of_range_index(files):
    controller = make_controller(files, inputs=["99"])
    controller.model.register_sample("S-001", "A", 0.5, 0.9, initial_stock=100)
    controller.model.reserve_order("S-001", "C1", 10)
    controller.model.go_to("approval")

    result = controller.dispatch("2")

    assert result is True
    assert controller.view.errors


def test_shipment_ship_lists_confirmed_orders_then_prompts_index_and_ships(files):
    controller = make_controller(files, inputs=["1"])
    controller.model.register_sample("S-001", "A", 0.5, 0.9, initial_stock=100)
    order = controller.model.reserve_order("S-001", "C1", 10)
    controller.model.approve_order(order["id"])
    controller.model.go_to("shipment")

    controller.dispatch("2")

    assert controller.view.prompts == ["번호: "]
    assert controller.model.list_shippable_orders() == []


def test_production_advance_prompts_minutes(files):
    controller = make_controller(files, inputs=["5"])
    controller.model.register_sample("S-001", "A", 0.8, 0.92, initial_stock=30)
    order = controller.model.reserve_order("S-001", "C1", 200)
    controller.model.approve_order(order["id"])
    controller.model.go_to("production")

    controller.dispatch("2")

    assert controller.view.prompts == ["진행 시간(분): "]
    item = controller.model.list_queue()[0]
    assert item["elapsed_minutes"] == 5
