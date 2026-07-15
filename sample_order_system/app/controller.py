"""SampleOrderController — 화면별 번호 선택 메뉴를 라우팅하고,
값이 필요한 동작은 필드마다 순차로 view.input()을 호출해 받는다."""

import mvc

from .formatting import format_sample_row, format_queue_row

_MAIN_MENU_SCREENS = {
    "1": "samples",
    "2": "reserve",
    "3": "approval",
    "4": "monitoring",
    "5": "production",
    "6": "shipment",
}


def _format_order_row(order):
    return f"{order['id']} | {order['sample_id']} | {order['customer']} | {order['quantity']} | {order['status']}"


class SampleOrderController(mvc.Controller):
    def dispatch(self, command, *args):
        try:
            return self._dispatch(command, *args)
        except ValueError as exc:
            self.view.show_error(str(exc))
            return True

    def _dispatch(self, command, *args):
        screen = self.model.screen
        if screen == "main":
            return self._dispatch_main(command)
        if screen == "samples":
            return self._dispatch_samples(command)
        if screen == "reserve":
            return self._dispatch_reserve(command)
        if screen == "approval":
            return self._dispatch_approval(command)
        if screen == "monitoring":
            return self._dispatch_monitoring(command)
        if screen == "production":
            return self._dispatch_production(command)
        if screen == "shipment":
            return self._dispatch_shipment(command)
        raise ValueError(f"알 수 없는 화면입니다: {screen!r}")

    def _back_to_main(self):
        self.model.go_to("main")
        return True

    def _prompt(self, label):
        return self.view.input(f"{label}: ").strip()

    def _select_from(self, records, empty_message):
        if not records:
            self.view.show_message(empty_message)
            return None
        for index, record in enumerate(records, start=1):
            self.view.show_message(f"[{index}] {_format_order_row(record)}")
        choice = self._prompt("번호")
        try:
            index = int(choice) - 1
        except ValueError:
            raise ValueError("번호는 숫자로 입력해야 합니다.")
        if not (0 <= index < len(records)):
            raise ValueError("목록에 없는 번호입니다.")
        return records[index]["id"]

    # -- main --
    def _dispatch_main(self, command):
        if command == "0":
            return False
        if command in _MAIN_MENU_SCREENS:
            self.model.go_to(_MAIN_MENU_SCREENS[command])
            return True
        self.view.show_error("잘못된 메뉴 번호입니다.")
        return True

    # -- samples --
    def _dispatch_samples(self, command):
        if command == "0":
            return self._back_to_main()
        if command == "1":
            sample_id = self._prompt("Sample ID")
            name = self._prompt("Name")
            avg_time = self._prompt("Avg Production Time")
            yield_rate = self._prompt("Yield Rate")
            stock = self._prompt("Initial Stock")
            self.model.register_sample(
                sample_id, name, float(avg_time), float(yield_rate),
                int(stock) if stock else 0,
            )
            self.view.show_message("시료가 등록되었습니다.")
            return True
        if command == "2":
            for sample in self.model.list_samples():
                self.view.show_message(format_sample_row(sample))
            return True
        if command == "3":
            keyword = self._prompt("Keyword")
            for sample in self.model.search_samples(keyword):
                self.view.show_message(format_sample_row(sample))
            return True
        self.view.show_error("잘못된 번호입니다.")
        return True

    # -- reserve --
    def _dispatch_reserve(self, command):
        if command == "0":
            return self._back_to_main()
        if command == "1":
            sample_id = self._prompt("Sample ID")
            customer = self._prompt("Customer")
            quantity = self._prompt("Quantity")
            order = self.model.reserve_order(sample_id, customer, int(quantity))
            self.view.show_message(f"예약 완료: {order['id']} ({order['status']})")
            return True
        self.view.show_error("잘못된 번호입니다.")
        return True

    # -- approval --
    def _dispatch_approval(self, command):
        if command == "0":
            return self._back_to_main()
        if command == "1":
            for order in self.model.list_reserved_orders():
                self.view.show_message(_format_order_row(order))
            return True
        if command == "2":
            order_id = self._select_from(
                self.model.list_reserved_orders(), "접수된 주문이 없습니다.",
            )
            if order_id is None:
                return True
            order = self.model.approve_order(order_id)
            self.view.show_message(f"승인 완료: {order['id']} -> {order['status']}")
            return True
        if command == "3":
            order_id = self._select_from(
                self.model.list_reserved_orders(), "접수된 주문이 없습니다.",
            )
            if order_id is None:
                return True
            order = self.model.reject_order(order_id)
            self.view.show_message(f"거절 완료: {order['id']} -> {order['status']}")
            return True
        self.view.show_error("잘못된 번호입니다.")
        return True

    # -- monitoring --
    def _dispatch_monitoring(self, command):
        if command == "0":
            return self._back_to_main()
        if command == "1":
            self.view.show_message(str(self.model.order_counts()))
            return True
        if command == "2":
            for level in self.model.stock_levels():
                self.view.show_message(str(level))
            return True
        self.view.show_error("잘못된 번호입니다.")
        return True

    # -- production --
    def _dispatch_production(self, command):
        if command == "0":
            return self._back_to_main()
        if command == "1":
            for item in self.model.list_queue():
                self.view.show_message(format_queue_row(item))
            return True
        if command == "2":
            minutes = self._prompt("진행 시간(분)")
            completed = self.model.advance_production(float(minutes))
            if completed:
                self.view.show_message(f"생산 완료: {completed['id']}")
            else:
                self.view.show_message("진행 중입니다.")
            return True
        self.view.show_error("잘못된 번호입니다.")
        return True

    # -- shipment --
    def _dispatch_shipment(self, command):
        if command == "0":
            return self._back_to_main()
        if command == "1":
            for order in self.model.list_shippable_orders():
                self.view.show_message(_format_order_row(order))
            return True
        if command == "2":
            order_id = self._select_from(
                self.model.list_shippable_orders(), "출고 가능한 주문이 없습니다.",
            )
            if order_id is None:
                return True
            order = self.model.ship_order(order_id)
            self.view.show_message(f"출고 완료: {order['id']} -> {order['status']}")
            return True
        self.view.show_error("잘못된 번호입니다.")
        return True
