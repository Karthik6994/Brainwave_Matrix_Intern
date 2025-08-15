def is_positive_float(value: str) -> bool:
    try:
        return float(value) >= 0
    except Exception:
        return False

def is_non_negative_int(value: str) -> bool:
    try:
        return int(value) >= 0
    except Exception:
        return False

def is_positive_int(value: str) -> bool:
    try:
        return int(value) > 0
    except Exception:
        return False
