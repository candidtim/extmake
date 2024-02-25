def _split_kv(kv: str) -> tuple[str, str]:
    if "=" not in kv:
        raise ValueError(f"Invalid key-value pair: {kv}")
    return kv.split("=", 1)


def parse(dsn: str) -> dict[str, str]:
    """Parse a DSN string into a dictionary."""
    return dict(_split_kv(kv) for kv in dsn.split(";") if kv)
