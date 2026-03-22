"""
Reusable HTTP client for all backend API endpoints.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Use a session to bypass any system HTTP proxy for local API calls
_session = requests.Session()
_session.trust_env = False  # ignore http_proxy / https_proxy env vars


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _handle(resp: requests.Response) -> dict | list | None:
    """Return JSON on success, raise on failure."""
    if resp.status_code in (200, 201):
        return resp.json()
    return None


def _error_detail(resp: requests.Response) -> str:
    """Extract error detail from a failed API response."""
    try:
        data = resp.json()
        if isinstance(data, dict):
            detail = data.get("detail", "")
            if isinstance(detail, list):
                msgs = [d.get("msg", str(d)) for d in detail]
                return "; ".join(msgs)
            return str(detail)
    except Exception:
        pass
    return f"Server returned {resp.status_code}"


# ══════════════════════════════════════════
#  Authentication
# ══════════════════════════════════════════

def api_login(username: str, password: str) -> dict | None:
    try:
        r = _session.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()
        return None
    except requests.RequestException:
        return None


def api_bootstrap(username: str, email: str, password: str, full_name: str, farm_ids: list[str] = None) -> dict | None:
    try:
        r = _session.post(
            f"{BASE_URL}/api/v1/auth/bootstrap",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name,
                "role": "admin",
                "farm_ids": farm_ids or [],
            },
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()
        return None
    except requests.RequestException:
        return None


def api_register(token: str, username: str, email: str, password: str,
                 full_name: str, role: str = "user", farm_ids: list[str] = None) -> tuple[dict | None, str]:
    """Register a new user. Returns (data, error_message)."""
    try:
        r = _session.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name,
                "role": role,
                "farm_ids": farm_ids or [],
            },
            headers=_headers(token),
            timeout=10,
        )
        if r.status_code in (200, 201):
            return r.json(), ""
        return None, _error_detail(r)
    except requests.RequestException as e:
        return None, f"Connection error: {e}"


def api_get_me(token: str) -> dict | None:
    try:
        r = _session.get(f"{BASE_URL}/api/v1/auth/me", headers=_headers(token), timeout=10)
        return _handle(r)
    except requests.RequestException:
        return None


def api_get_users(token: str) -> list | None:
    try:
        r = _session.get(f"{BASE_URL}/api/v1/auth/users", headers=_headers(token), timeout=10)
        return _handle(r)
    except requests.RequestException:
        return None


def api_update_user(token: str, username: str, data: dict) -> dict | None:
    try:
        r = _session.put(
            f"{BASE_URL}/api/v1/auth/users/{username}",
            json=data,
            headers=_headers(token),
            timeout=10,
        )
        return _handle(r)
    except requests.RequestException:
        return None


def api_deactivate_user(token: str, username: str) -> dict | None:
    try:
        r = _session.delete(
            f"{BASE_URL}/api/v1/auth/users/{username}",
            headers=_headers(token),
            timeout=10,
        )
        return _handle(r)
    except requests.RequestException:
        return None


# ══════════════════════════════════════════
#  Cattle
# ══════════════════════════════════════════

def api_get_cattle_list(token: str) -> list | None:
    try:
        r = _session.get(f"{BASE_URL}/api/v1/cattle", headers=_headers(token), timeout=10)
        return _handle(r)
    except requests.RequestException:
        return None


def api_get_cattle(token: str, cid: int) -> dict | None:
    try:
        r = _session.get(f"{BASE_URL}/api/v1/cattle/{cid}", headers=_headers(token), timeout=10)
        return _handle(r)
    except requests.RequestException:
        return None


def api_create_cattle(token: str, cid: int, name: str, farm_id: str,
                      breed: str, age: int, status: str = "active") -> dict | None:
    try:
        r = _session.post(
            f"{BASE_URL}/api/v1/cattle",
            json={"cid": cid, "name": name, "farm_id": farm_id, "breed": breed, "age": age, "status": status},
            headers=_headers(token),
            timeout=10,
        )
        return _handle(r)
    except requests.RequestException:
        return None


def api_update_cattle(token: str, cid: int, data: dict) -> dict | None:
    try:
        r = _session.put(
            f"{BASE_URL}/api/v1/cattle/{cid}",
            json=data,
            headers=_headers(token),
            timeout=10,
        )
        return _handle(r)
    except requests.RequestException:
        return None


# ══════════════════════════════════════════
#  Sensor Data
# ══════════════════════════════════════════

def api_get_all_latest(token: str) -> list | None:
    try:
        r = _session.get(f"{BASE_URL}/api/v1/cattle/latest", headers=_headers(token), timeout=15)
        return _handle(r)
    except requests.RequestException:
        return None


def api_get_cattle_latest(token: str, cid: int) -> dict | None:
    try:
        r = _session.get(f"{BASE_URL}/api/v1/cattle/{cid}/latest", headers=_headers(token), timeout=10)
        return _handle(r)
    except requests.RequestException:
        return None


def api_get_cattle_recent(token: str, cid: int, limit: int = 100) -> list | None:
    try:
        r = _session.get(
            f"{BASE_URL}/api/v1/cattle/{cid}/recent",
            params={"limit": limit},
            headers=_headers(token),
            timeout=15,
        )
        return _handle(r)
    except requests.RequestException:
        return None


def api_get_cattle_last_hour(token: str, cid: int) -> list | None:
    try:
        r = _session.get(
            f"{BASE_URL}/api/v1/cattle/{cid}/last-hour",
            headers=_headers(token),
            timeout=15,
        )
        return _handle(r)
    except requests.RequestException:
        return None


def api_get_cattle_range(token: str, cid: int, start: str, end: str) -> list | None:
    try:
        r = _session.get(
            f"{BASE_URL}/api/v1/cattle/{cid}/range",
            params={"start": start, "end": end},
            headers=_headers(token),
            timeout=15,
        )
        return _handle(r)
    except requests.RequestException:
        return None


# ══════════════════════════════════════════
#  Health Events
# ══════════════════════════════════════════

def api_get_health_events(token: str, cid: int, limit: int = 50) -> list | None:
    try:
        r = _session.get(
            f"{BASE_URL}/api/v1/cattle/{cid}/health-events",
            params={"limit": limit},
            headers=_headers(token),
            timeout=10,
        )
        return _handle(r)
    except requests.RequestException:
        return None


def api_get_recent_health_events(token: str, limit: int = 50) -> list | None:
    try:
        r = _session.get(
            f"{BASE_URL}/api/v1/health-events/recent",
            params={"limit": limit},
            headers=_headers(token),
            timeout=10,
        )
        return _handle(r)
    except requests.RequestException:
        return None


# ══════════════════════════════════════════
#  Alerts
# ══════════════════════════════════════════

def api_evaluate_cattle(token: str, cid: int) -> dict | None:
    try:
        r = _session.post(
            f"{BASE_URL}/api/v1/alerts/evaluate/{cid}",
            headers=_headers(token),
            timeout=15,
        )
        return _handle(r)
    except requests.RequestException:
        return None


def api_evaluate_all(token: str) -> dict | None:
    try:
        r = _session.post(
            f"{BASE_URL}/api/v1/alerts/evaluate-all",
            headers=_headers(token),
            timeout=30,
        )
        return _handle(r)
    except requests.RequestException:
        return None


def api_get_cattle_alerts(token: str, cid: int, limit: int = 50) -> list | None:
    try:
        r = _session.get(
            f"{BASE_URL}/api/v1/alerts/{cid}",
            params={"limit": limit},
            headers=_headers(token),
            timeout=10,
        )
        return _handle(r)
    except requests.RequestException:
        return None


def api_get_recent_alerts(token: str, limit: int = 50) -> list | None:
    try:
        r = _session.get(
            f"{BASE_URL}/api/v1/alerts/recent/all",
            params={"limit": limit},
            headers=_headers(token),
            timeout=10,
        )
        return _handle(r)
    except requests.RequestException:
        return None


def api_get_alert_counter(token: str, cid: int) -> dict | None:
    try:
        r = _session.get(
            f"{BASE_URL}/api/v1/alerts/{cid}/counter",
            headers=_headers(token),
            timeout=10,
        )
        return _handle(r)
    except requests.RequestException:
        return None
