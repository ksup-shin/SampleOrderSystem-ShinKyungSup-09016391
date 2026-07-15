"""SampleOrderView — 화면 상태에 맞는 번호 선택 메뉴를 콘솔에 출력한다."""

import mvc

from .menus import MENUS_BY_SCREEN

_TITLES = {
    "main": "===== 반도체 시료 생산주문관리 시스템 =====",
    "samples": "----- 시료 관리 -----",
    "reserve": "----- 시료 주문 -----",
    "approval": "----- 주문 승인/거절 -----",
    "monitoring": "----- 모니터링 -----",
    "production": "----- 생산 라인 조회 -----",
    "shipment": "----- 출고 처리 -----",
}


class SampleOrderView(mvc.View):
    def render(self, model):
        self.print(_TITLES.get(model.screen, ""))
        for number, label in MENUS_BY_SCREEN.get(model.screen, []):
            self.print(f"[{number}] {label}")
        if model.screen == "main":
            summary = model.summary()
            self.print(
                f"등록 시료 {summary['sample_count']}종 | 총 재고 {summary['total_stock']} | "
                f"전체 주문 {summary['order_count']}건 | 생산라인 대기 {summary['queue_length']}건"
            )
