import os
from supabase import create_client, Client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL و SUPABASE_KEY تنظیم نشده‌اند."
    )


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================
# USERS
# =========================

def get_or_create_user(
    telegram_id: int,
    username: str | None,
    first_name: str | None,
    last_name: str | None
):
    result = (
        supabase
        .table("users")
        .select("*")
        .eq("telegram_id", telegram_id)
        .execute()
    )

    if result.data:
        user = result.data[0]

        supabase.table("users").update({
            "username": username,
            "first_name": first_name,
            "last_name": last_name
        }).eq(
            "telegram_id", telegram_id
        ).execute()

        return user

    result = (
        supabase
        .table("users")
        .insert({
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name
        })
        .execute()
    )

    return result.data[0]


def get_user_by_telegram_id(telegram_id: int):
    result = (
        supabase
        .table("users")
        .select("*")
        .eq("telegram_id", telegram_id)
        .maybe_single()
        .execute()
    )

    return result.data


# =========================
# SETTINGS
# =========================

def get_setting(key: str, default=None):
    result = (
        supabase
        .table("settings")
        .select("value")
        .eq("key", key)
        .maybe_single()
        .execute()
    )

    if not result.data:
        return default

    return result.data.get("value", default)


def set_setting(key: str, value: str):
    return (
        supabase
        .table("settings")
        .upsert({
            "key": key,
            "value": value
        })
        .execute()
    )


# =========================
# SERVICES
# =========================

def get_active_services():
    result = (
        supabase
        .table("services")
        .select("*")
        .eq("is_active", True)
        .order("created_at", desc=True)
        .execute()
    )

    return result.data


def get_service(service_id: str):
    result = (
        supabase
        .table("services")
        .select("*")
        .eq("id", service_id)
        .maybe_single()
        .execute()
    )

    return result.data


def create_service(
    name: str,
    description: str,
    volume: str,
    duration: str,
    price: int
):
    result = (
        supabase
        .table("services")
        .insert({
            "name": name,
            "description": description,
            "volume": volume,
            "duration": duration,
            "price": price,
            "is_active": True
        })
        .execute()
    )

    return result.data[0]


def update_service(service_id: str, data: dict):
    return (
        supabase
        .table("services")
        .update(data)
        .eq("id", service_id)
        .execute()
    )


# =========================
# ORDERS
# =========================

def create_order(
    user_id: str,
    service_id: str,
    amount: int
):
    result = (
        supabase
        .table("orders")
        .insert({
            "user_id": user_id,
            "service_id": service_id,
            "amount": amount,
            "status": "waiting_receipt"
        })
        .execute()
    )

    return result.data[0]


def get_order(order_id: str):
    result = (
        supabase
        .table("orders")
        .select(
            "*, users(*), services(*)"
        )
        .eq("id", order_id)
        .maybe_single()
        .execute()
    )

    return result.data


def update_order(order_id: str, data: dict):
    return (
        supabase
        .table("orders")
        .update(data)
        .eq("id", order_id)
        .execute()
    )
