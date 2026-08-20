from core import device_info


def min_ram_for_version(version: str) -> int:
    try:
        main = int(version.split(".")[1])
    except Exception:
        return 2048
    if main >= 18:
        return 2048
    if main >= 16:
        return 1536
    return 1024


def recommend_ram(total_mb: int, available_mb: int) -> int:
    if total_mb <= 0:
        return 2048
    # Always keep head-room for Android + Termux
    safe_budget = total_mb - max(int(total_mb * 0.30), 1024)
    if available_mb > 0:
        safe_budget = min(safe_budget, available_mb)
    if total_mb <= 3072:
        return max(1024, min(1536, safe_budget))
    if total_mb <= 4096:
        return max(1536, min(2560, safe_budget))
    if total_mb <= 6144:
        return max(2048, min(3584, safe_budget))
    if total_mb <= 8192:
        return max(3072, min(4608, safe_budget))
    return max(4096, min(6144, safe_budget))


def is_dangerous(amount_mb: int, total_mb: int, available_mb: int) -> bool:
    if total_mb <= 0:
        return amount_mb > 8192
    estimated = total_mb - amount_mb
    return estimated < 1536 or amount_mb > total_mb - 512 or (available_mb > 0 and amount_mb > available_mb)


def is_too_low(amount_mb: int, version: str) -> bool:
    return amount_mb < min_ram_for_version(version)