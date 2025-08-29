from datetime import datetime, UTC


def utc_signed_now():
    return datetime.now(UTC)
