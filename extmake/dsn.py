def parse(dsn: str) -> dict[str, str]:
    """Parse a DSN string into a dictionary."""
    return dict(kv.split("=", 1) for kv in dsn.split(";"))
