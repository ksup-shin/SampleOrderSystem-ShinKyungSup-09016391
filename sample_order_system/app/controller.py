"""SampleOrderController — 화면별 번호 선택 메뉴를 라우팅하고,
값이 필요한 동작은 필드마다 순차로 view.input()을 호출해 받는다.
목록/현황 출력은 formatting.py의 표 함수를 거쳐 한 번에 출력한다."""

import mvc

from . import formatting

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

    def _select_order(self, records, empty_message):
        if not records:
            self.view.show_message(empty_message)
            return None
        self.view.show_message(formatting.format_indexed_orders_table(records))
        choice = self._prompt("번호")
        try:
            index = int(choice) - 1
        except ValueError:
            raise ValueError("번호는 숫자로 입력해야 합니다.")
        if not (0 <= index < len(records)):
            raise ValueError("목록에 없는 번호입니다.")
        return records[index]["id"]

    def _show_status_transition(self, before_status, order):
        self.view.show_message(formatting.format_orders_table([order]))
        self.view.show_message(f"상태 변경: {before_status} → {order['status']}")

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
            sample_id = self._prompt("시료 ID")
            name = self._prompt("이름")
            avg_time = self._prompt("평균 생산시간(분)")
            yield_rate = self._prompt("수율")
            stock = self._prompt("초기 재고")
            self.model.register_sample(
                sample_id, name, float(avg_time), float(yield_rate),
                int(stock) if stock else 0,
            )
            self.view.show_message("시료가 등록되었습니다.")
            return True
        if command == "2":
            self.view.show_message(formatting.format_samples_table(self.model.list_samples()))
            return True
        if command == "3":
            keyword = self._prompt("시료 이름")
            self.view.show_message(formatting.format_samples_table(self.model.search_samples(keyword)))
            return True
        self.view.show_error("잘못된 번호입니다.")
        return True

    # -- reserve --
    def _dispatch_reserve(self, command):
        if command == "0":
            return self._back_to_main()
        if command == "1":
            sample_id = self._prompt("시료 ID")
            customer = self._prompt("고객명")
            quantity = self._prompt("수량")
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
            self.view.show_message(
                formatting.format_orders_table(self.model.list_reserved_orders())
            )
            return True
        if command == "2":
            order_id = self._select_order(
                self.model.list_reserved_orders(), "접수된 주문이 없습니다.",
            )
            if order_id is None:
                return True
            order = self.model.approve_order(order_id)
            self._show_status_transition("RESERVED", order)
            return True
        if command == "3":
            order_id = self._select_order(
                self.model.list_reserved_orders(), "접수된 주문이 없습니다.",
            )
            if order_id is None:
                return True
            order = self.model.reject_order(order_id)
            self._show_status_transition("RESERVED", order)
            return True
        self.view.show_error("잘못된 번호입니다.")
        return True

    # -- monitoring --
    def _dispatch_monitoring(self, command):
        if command == "0":
            return self._back_to_main()
        if command == "1":
            self.view.show_message(formatting.format_order_counts_table(self.model.order_counts()))
            return True
        if command == "2":
            self.view.show_message(formatting.format_stock_levels_table(self.model.stock_levels()))
            return True
        self.view.show_error("잘못된 번호입니다.")
        return True

    # -- production --
    def _dispatch_production(self, command):
        if command == "0":
            return self._back_to_main()
        if command == "1":
            status = self.model.production_status()
            if status["current"] is None:
                self.view.show_message("현재 생산 중인 주문이 없습니다.")
            else:
                self.view.show_message("[생산 중]")
                self.view.show_message(formatting.format_production_current_table(status["current"]))
            if status["waiting"]:
                self.view.show_message("[대기 중]")
                self.view.show_message(formatting.format_production_waiting_table(status["waiting"]))
            else:
                self.view.show_message("대기 중인 주문이 없습니다.")
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
            self.view.show_message(
                formatting.format_orders_table(self.model.list_shippable_orders())
            )
            return True
        if command == "2":
            order_id = self._select_order(
                self.model.list_shippable_orders(), "출고 가능한 주문이 없습니다.",
            )
            if order_id is None:
                return True
            order = self.model.ship_order(order_id)
            self._show_status_transition("CONFIRMED", order)
            return True
        self.view.show_error("잘못된 번호입니다.")
        return True
