"""Payment config and plan pricing from .streamlit/secrets.toml (PAYMENTS). No hardcoded numbers."""
import streamlit as st


def _get_payments_secret() -> dict:
    """Return PAYMENTS from secrets; support both nested and flat keys. Safe when secrets missing."""
    try:
        raw = st.secrets.get("PAYMENTS")
    except Exception:
        return {}
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    return {}


def get_payment_config() -> dict:
    """
    Return dict with gcash, maya, plans, free_daily_limit, premium_daily_limit.
    Keys may be nested (e.g. plans.premium) or flat (e.g. plans_premium_price_php) depending on secrets.
    """
    p = _get_payments_secret()
    # Normalize to flat structure for UI
    gcash = p.get("gcash")
    if isinstance(gcash, dict):
        gcash_number = gcash.get("number", "")
        gcash_name = gcash.get("name", "")
    else:
        gcash_number = p.get("gcash_number", "")
        gcash_name = p.get("gcash_name", "")

    maya = p.get("maya")
    if isinstance(maya, dict):
        maya_number = maya.get("number", "")
        maya_name = maya.get("name", "")
    else:
        maya_number = p.get("maya_number", "")
        maya_name = p.get("maya_name", "")

    plans = p.get("plans") or {}
    if not isinstance(plans, dict):
        plans = {}
    premium_plan = plans.get("premium") or {}
    pro_plan = plans.get("pro") or {}
    if isinstance(premium_plan, dict):
        premium_price = premium_plan.get("price_php", 199)
        premium_billing = premium_plan.get("billing", "Month")
    else:
        premium_price = p.get("premium_price_php", 199)
        premium_billing = p.get("premium_billing", "Month")
    if isinstance(pro_plan, dict):
        pro_price = pro_plan.get("price_php", 999)
        pro_billing = pro_plan.get("billing", "monthly")
    else:
        pro_price = p.get("pro_price_php", 999)
        pro_billing = p.get("pro_billing", "monthly")

    # Support nested PAYMENTS.free_daily_limit or top-level PAYMENTS_free_daily_limit
    try:
        free_limit = p.get("free_daily_limit") or st.secrets.get("PAYMENTS_free_daily_limit", 2)
        premium_limit = p.get("premium_daily_limit") or st.secrets.get("PAYMENTS_premium_daily_limit", 9999)
    except Exception:
        free_limit = 2
        premium_limit = 9999
    try:
        free_limit = int(free_limit)
    except (TypeError, ValueError):
        free_limit = 2
    try:
        premium_limit = int(premium_limit)
    except (TypeError, ValueError):
        premium_limit = 9999

    return {
        "gcash_number": gcash_number,
        "gcash_name": gcash_name,
        "maya_number": maya_number,
        "maya_name": maya_name,
        "premium_price_php": premium_price,
        "premium_billing": premium_billing,
        "pro_price_php": pro_price,
        "pro_billing": pro_billing,
        "free_daily_limit": free_limit,
        "premium_daily_limit": premium_limit,
    }


def get_plans_config() -> list:
    """Return list of plan dicts for Pricing page. Prices/limits from secrets (PAYMENTS)."""
    pay = get_payment_config()
    return [
        {
            "key": "free",
            "name": "Free",
            "price_php": 0,
            "billing": "",
            "features": [
                f"{pay['free_daily_limit']} checks per day",
                "Basic verdict & reasons",
                "Shareable warning text",
                "No screenshot upload",
            ],
        },
        {
            "key": "premium",
            "name": "Premium",
            "price_php": pay["premium_price_php"],
            "billing": pay["premium_billing"],
            "features": [
                "Unlimited checks",
                "Advanced explainers",
                "Priority support",
            ],
        },
        {
            "key": "pro",
            "name": "Pro",
            "price_php": pay["pro_price_php"],
            "billing": pay["pro_billing"],
            "features": [
                "Everything in Premium",
                "Priority verification",
                "Bulk check (coming soon)",
                "Dedicated support",
            ],
        },
    ]
