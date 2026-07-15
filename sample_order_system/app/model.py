"""SampleOrderModel — mvc.Model 위의 얇은 퍼사드. 상태는 JSON 파일에 있고,
이 클래스는 화면 전환 상태(screen)만 보유한다."""

from poc_json import read_all

import mvc

from ..paths import SAMPLES_FILE, ORDERS_FILE, PRODUCTION_QUEUE_FILE
from ..samples import repository as samples
from ..orders import repository as orders
from ..orders import approval
from ..orders import shipment
from ..production import queue as production_queue
from ..production import service as production_service
from ..monitoring import service as monitoring
from .formatting import format_summary


class SampleOrderModel(mvc.Model):
    def __init__(
        self, samples_file=SAMPLES_FILE, orders_file=ORDERS_FILE,
        queue_file=PRODUCTION_QUEUE_FILE,
    ):
        super().__init__()
        self.screen = "main"
        self.samples_file = samples_file
        self.orders_file = orders_file
        self.queue_file = queue_file

    def go_to(self, screen):
        self.screen = screen
        self.notify("screen_changed", screen)

    # -- 시료 --
    def register_sample(self, sample_id, name, avg_production_time, yield_rate, initial_stock=0):
        result = samples.register_sample(
            sample_id, name, avg_production_time, yield_rate,
            initial_stock=initial_stock, file_path=self.samples_file,
        )
        self.notify("sample_registered", result)
        return result

    def list_samples(self):
        return samples.list_samples(file_path=self.samples_file)

    def search_samples(self, keyword):
        return samples.search_samples(keyword, file_path=self.samples_file)

    # -- 주문 예약 --
    def reserve_order(self, sample_id, customer, quantity):
        result = orders.reserve_order(
            sample_id, customer, quantity,
            orders_file=self.orders_file, samples_file=self.samples_file,
        )
        self.notify("order_reserved", result)
        return result

    # -- 승인/거절 --
    def list_reserved_orders(self):
        return orders.list_orders(status="RESERVED", file_path=self.orders_file)

    def preview_approval(self, order_id):
        return approval.preview_approval(
            order_id, orders_file=self.orders_file,
            samples_file=self.samples_file, queue_file=self.queue_file,
        )

    def approve_order(self, order_id):
        result = approval.approve_order(
            order_id, orders_file=self.orders_file,
            samples_file=self.samples_file, queue_file=self.queue_file,
        )
        self.notify("order_approved", result)
        return result

    def reject_order(self, order_id):
        result = approval.reject_order(order_id, orders_file=self.orders_file)
        self.notify("order_rejected", result)
        return result

    # -- 생산 라인 --
    def list_queue(self):
        return production_queue.list_queue(file_path=self.queue_file)

    def advance_production(self, minutes):
        result = production_service.advance_production(
            minutes, queue_file=self.queue_file,
            samples_file=self.samples_file, orders_file=self.orders_file,
        )
        self.notify("production_advanced", result)
        return result

    # -- 출고 --
    def list_shippable_orders(self):
        return shipment.list_shippable_orders(orders_file=self.orders_file)

    def ship_order(self, order_id):
        result = shipment.ship_order(
            order_id, orders_file=self.orders_file, samples_file=self.samples_file,
        )
        self.notify("order_shipped", result)
        return result

    # -- 모니터링 --
    def order_counts(self):
        return monitoring.order_counts_by_status(orders_file=self.orders_file)

    def stock_levels(self):
        return monitoring.stock_levels(
            samples_file=self.samples_file, orders_file=self.orders_file,
        )

    def summary(self):
        return format_summary(
            self.list_samples(), read_all(self.orders_file), self.list_queue(),
        )
