import base64


def check_key(key: str) -> bool:
    """Return True if the key is a valid AES key (base64, 16-byte aligned)."""
    try:
        return not (len(key) % 4 or len(base64.b64decode(key)) % 16)
    except Exception:  # noqa: BLE001
        return False


def format_size(num_bytes: int) -> str:
    """Return a human-readable file size, e.g. 1536 -> "1.5 KB"."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{int(size)} B" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"
