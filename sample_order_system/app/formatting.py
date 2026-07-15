"""콘솔 출력용 순수 포맷팅 함수 (I/O 없음, pytest로 직접 검증 가능)."""


def format_sample_row(sample):
    return (
        f"{sample['id']} | {sample['name']} | "
        f"{sample['avg_production_time']} | {sample['yield_rate']} | {sample['stock']}"
    )


def format_summary(samples, orders, queue):
    return {
        "sample_count": len(samples),
        "total_stock": sum(sample["stock"] for sample in samples),
        "order_count": len(orders),
        "queue_length": len(queue),
    }


def format_queue_row(item):
    total = item["total_minutes"]
    progress = item["elapsed_minutes"] / total if total else 1.0
    remaining = total - item["elapsed_minutes"]
    return (
        f"{item['id']} | {item['sample_id']} | 주문량 {item['order_quantity']} | "
        f"부족분 {item['shortage']} | 실생산량 {item['actual_quantity']} | "
        f"진행율 {progress:.0%} | 남은시간 {remaining:.1f}분"
    )
