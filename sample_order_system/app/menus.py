"""화면별 (번호, 라벨) 메뉴 정의 — view(출력)와 controller(라우팅 근거)가 함께 참조하는 단일 출처."""

MAIN_MENU = [
    ("1", "시료 관리"),
    ("2", "시료 주문"),
    ("3", "주문 승인/거절"),
    ("4", "모니터링"),
    ("5", "생산 라인 조회"),
    ("6", "출고 처리"),
    ("0", "종료"),
]

SAMPLES_MENU = [
    ("1", "시료 등록"),
    ("2", "시료 조회"),
    ("3", "시료 검색"),
    ("0", "뒤로"),
]

RESERVE_MENU = [
    ("1", "시료 예약"),
    ("0", "뒤로"),
]

APPROVAL_MENU = [
    ("1", "접수된 주문 목록"),
    ("2", "주문 승인"),
    ("3", "주문 거절"),
    ("0", "뒤로"),
]

MONITORING_MENU = [
    ("1", "주문량 확인"),
    ("2", "재고량 확인"),
    ("0", "뒤로"),
]

PRODUCTION_MENU = [
    ("1", "생산 현황/대기열 조회"),
    ("2", "생산 진행 (테스트용: 임의의 시간(분)이 흐른 것으로 처리)"),
    ("0", "뒤로"),
]

SHIPMENT_MENU = [
    ("1", "출고 가능 목록"),
    ("2", "출고 처리"),
    ("0", "뒤로"),
]

MENUS_BY_SCREEN = {
    "main": MAIN_MENU,
    "samples": SAMPLES_MENU,
    "reserve": RESERVE_MENU,
    "approval": APPROVAL_MENU,
    "monitoring": MONITORING_MENU,
    "production": PRODUCTION_MENU,
    "shipment": SHIPMENT_MENU,
}
