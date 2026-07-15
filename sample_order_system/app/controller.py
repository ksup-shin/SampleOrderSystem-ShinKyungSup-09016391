"""SampleOrderController — 화면 상태에 따라 명령을 라우팅한다."""

import mvc

from .formatting import format_queue_row

_MAIN_MENU_SCREENS = {
    "1": "samples",
    "2": "reserve",
    "3": "approval",
    "4": "monitoring",
    "5": "production",
    "6": "shipment",
}


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
            return self._dispatch_samples(command, *args)
        if screen == "reserve":
            return self._dispatch_reserve(command, *args)
        if screen == "approval":
            return self._dispatch_approval(command, *args)
        if screen == "monitoring":
            return self._dispatch_monitoring(command)
        if screen == "production":
            return self._dispatch_production(command, *args)
        if screen == "shipment":
            return self._dispatch_shipment(command, *args)
        raise ValueError(f"알 수 없는 화면입니다: {screen!r}")

    def _back_to_main(self):
        self.model.go_to("main")
        return True

    def _dispatch_main(self, command):
        if command == "0":
            return False
        if command in _MAIN_MENU_SCREENS:
            self.model.go_to(_MAIN_MENU_SCREENS[command])
            return True
        self.view.show_error("잘못된 메뉴 번호입니다.")
        return True

    def _dispatch_samples(self, command, *args):
        if command == "0":
            return self._back_to_main()
        if command == "register":
            sample_id, name, avg_time, yield_rate, *rest = args
            stock = int(rest[0]) if rest else 0
            self.model.register_sample(sample_id, name, float(avg_time), float(yield_rate), stock)
            self.view.show_message("시료가 등록되었습니다.")
            return True
        if command == "list":
            for sample in self.model.list_samples():
                self.view.show_message(str(sample))
            return True
        if command == "search":
            (keyword,) = args
            for sample in self.model.search_samples(keyword):
                self.view.show_message(str(sample))
            return True
        self.view.show_error("알 수 없는 명령입니다.")
        return True

    def _dispatch_reserve(self, command, *args):
        if command == "0":
            return self._back_to_main()
        if command == "reserve":
            sample_id, customer, quantity = args
            order = self.model.reserve_order(sample_id, customer, int(quantity))
            self.view.show_message(f"예약 완료: {order['id']} ({order['status']})")
            return True
        self.view.show_error("알 수 없는 명령입니다.")
        return True

    def _dispatch_approval(self, command, *args):
        if command == "0":
            return self._back_to_main()
        if command == "list":
            for order in self.model.list_reserved_orders():
                self.view.show_message(str(order))
            return True
        if command == "approve":
            (order_id,) = args
            order = self.model.approve_order(order_id)
            self.view.show_message(f"승인 완료: {order['id']} -> {order['status']}")
            return True
        if command == "reject":
            (order_id,) = args
            order = self.model.reject_order(order_id)
            self.view.show_message(f"거절 완료: {order['id']} -> {order['status']}")
            return True
        self.view.show_error("알 수 없는 명령입니다.")
        return True

    def _dispatch_monitoring(self, command):
        if command == "0":
            return self._back_to_main()
        if command == "orders":
            self.view.show_message(str(self.model.order_counts()))
            return True
        if command == "stock":
            for level in self.model.stock_levels():
                self.view.show_message(str(level))
            return True
        self.view.show_error("알 수 없는 명령입니다.")
        return True

    def _dispatch_production(self, command, *args):
        if command == "0":
            return self._back_to_main()
        if command == "list":
            for item in self.model.list_queue():
                self.view.show_message(format_queue_row(item))
            return True
        if command == "advance":
            (minutes,) = args
            completed = self.model.advance_production(float(minutes))
            if completed:
                self.view.show_message(f"생산 완료: {completed['id']}")
            else:
                self.view.show_message("진행 중입니다.")
            return True
        self.view.show_error("알 수 없는 명령입니다.")
        return True

    def _dispatch_shipment(self, command, *args):
        if command == "0":
            return self._back_to_main()
        if command == "list":
            for order in self.model.list_shippable_orders():
                self.view.show_message(str(order))
            return True
        if command == "ship":
            (order_id,) = args
            order = self.model.ship_order(order_id)
            self.view.show_message(f"출고 완료: {order['id']} -> {order['status']}")
            return True
        self.view.show_error("알 수 없는 명령입니다.")
        return True
