"""Rate limits: free vs premium daily check limits."""
import streamlit as st
from db.queries import (
    ensure_user,
    get_user_plan,
    get_usage_today,
    record_usage,
    insert_scan,
)


def _get_limits():
    """Daily limits from secrets. Supports PAYMENTS.free_daily_limit or top-level PAYMENTS_free_daily_limit."""
    try:
        payments = st.secrets.get("PAYMENTS") or {}
    except Exception:
        return 2, 9999
    if isinstance(payments, dict):
        try:
            free = payments.get("free_daily_limit") or st.secrets.get("PAYMENTS_free_daily_limit", 2)
            premium = payments.get("premium_daily_limit") or st.secrets.get("PAYMENTS_premium_daily_limit", 9999)
        except Exception:
            return 2, 9999
    else:
        try:
            free = st.secrets.get("PAYMENTS_free_daily_limit", 2)
            premium = st.secrets.get("PAYMENTS_premium_daily_limit", 9999)
        except Exception:
            return 2, 9999
    try:
        free = int(free)
    except (TypeError, ValueError):
        free = 2
    try:
        premium = int(premium)
    except (TypeError, ValueError):
        premium = 9999
    return free, premium


def get_daily_limit(email: str) -> int:
    """Return max checks per day for this user (free vs premium/pro)."""
    if not email:
        free, _ = _get_limits()
        return free
    ensure_user(email)
    plan_info = get_user_plan(email)
    plan = (plan_info.get("plan") or "free").lower()
    premium_until = plan_info.get("premium_until")
    # If premium/pro but expired, treat as free
    if plan in ("premium", "pro") and premium_until:
        from datetime import datetime
        try:
            until = datetime.strptime(premium_until, "%Y-%m-%d").date()
            if until >= datetime.utcnow().date():
                _, premium = _get_limits()
                return premium
        except Exception:
            pass
    free, _ = _get_limits()
    return free


def can_user_check(email: str) -> tuple[bool, str]:
    """
    Return (True, "") if user can run a check; else (False, "reason").
    """
    limit = get_daily_limit(email)
    used = get_usage_today(email or "anonymous")
    if used >= limit:
        return False, f"You've used {used} of {limit} free checks today. Upgrade to Premium for unlimited checks."
    return True, ""


def record_check(
    email: str,
    verdict: str,
    confidence: int,
    category: str,
    signals_json: str,
    msg_hash: str,
) -> None:
    """Record usage and insert scan row (no raw message)."""
    record_usage(email or "anonymous")
    insert_scan(
        email=(email or "anonymous"),
        verdict=verdict,
        confidence=confidence,
        category=category or "",
        signals_json=signals_json or "[]",
        msg_hash=msg_hash or "",
    )
