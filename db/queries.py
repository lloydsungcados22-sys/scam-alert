"""CRUD for CheckMoYan. Uses Snowflake if [SNOWFLAKE] in secrets.toml, else SQLite."""
from . import schema

def _backend():
    if schema._use_snowflake():
        from . import queries_snowflake
        return queries_snowflake
    from . import queries_sqlite
    return queries_sqlite


def ensure_user(email: str) -> None:
    return _backend().ensure_user(email)


def get_user_plan(email: str) -> dict:
    return _backend().get_user_plan(email)


def set_user_plan(email: str, plan: str, premium_until: str = None) -> None:
    return _backend().set_user_plan(email, plan, premium_until)


def record_usage(email: str) -> None:
    return _backend().record_usage(email)


def get_usage_today(email: str) -> int:
    return _backend().get_usage_today(email)


def insert_scan(
    email: str,
    verdict: str,
    confidence: int,
    category: str,
    signals_json: str,
    msg_hash: str,
) -> int:
    return _backend().insert_scan(email, verdict, confidence, category, signals_json, msg_hash)


def get_stats_today() -> dict:
    return _backend().get_stats_today()


def get_trending_categories(limit: int = 5) -> list:
    return _backend().get_trending_categories(limit)


def insert_upgrade_request(
    email: str,
    plan: str,
    method: str,
    ref: str = None,
    receipt_path: str = None,
) -> int:
    return _backend().insert_upgrade_request(email, plan, method, ref, receipt_path)


def list_upgrade_requests(status: str = None) -> list:
    return _backend().list_upgrade_requests(status)


def get_upgrade_request(req_id: int) -> dict:
    return _backend().get_upgrade_request(req_id)


def update_upgrade_request(
    req_id: int,
    status: str,
    admin_notes: str = None,
    approved_until: str = None,
) -> None:
    return _backend().update_upgrade_request(req_id, status, admin_notes, approved_until)
