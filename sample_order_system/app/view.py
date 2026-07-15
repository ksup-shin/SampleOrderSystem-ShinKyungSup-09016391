"""SampleOrderView — 화면 상태에 따라 메뉴를 콘솔에 출력한다."""

import mvc

from .formatting import format_sample_row

_MENUS = {
    "main": [
        "===== 반도체 시료 생산주문관리 시스템 =====",
        "[1] 시료 관리   [2] 시료 주문   [3] 주문 승인/거절",
        "[4] 모니터링    [5] 생산 라인 조회   [6] 출고 처리",
        "[0] 종료",
    ],
    "samples": [
        "----- 시료 관리 -----",
        "register <id> <name> <avg_time> <yield> [stock] | list | search <keyword> | 0(뒤로)",
    ],
    "reserve": [
        "----- 시료 주문 -----",
        "reserve <sample_id> <customer> <quantity> | 0(뒤로)",
    ],
    "approval": [
        "----- 주문 승인/거절 -----",
        "list | approve <order_id> | reject <order_id> | 0(뒤로)",
    ],
    "monitoring": [
        "----- 모니터링 -----",
        "orders(상태별 건수) | stock(재고 현황) | 0(뒤로)",
    ],
    "production": [
        "----- 생산 라인 조회 -----",
        "list(대기열) | advance <minutes>(진행) | 0(뒤로)",
    ],
    "shipment": [
        "----- 출고 처리 -----",
        "list | ship <order_id> | 0(뒤로)",
    ],
}


class SampleOrderView(mvc.View):
    def render(self, model):
        for line in _MENUS.get(model.screen, []):
            self.print(line)
        if model.screen == "main":
            summary = model.summary()
            self.print(
                f"등록 시료 {summary['sample_count']}종 | 총 재고 {summary['total_stock']} | "
                f"전체 주문 {summary['order_count']}건 | 생산라인 대기 {summary['queue_length']}건"
            )

    def show_sample(self, sample):
        self.print(format_sample_row(sample))
