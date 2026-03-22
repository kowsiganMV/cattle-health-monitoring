#!/usr/bin/env python3
"""
Complete API Test Suite for CHM API
Tests all authentication, user management, cattle, sensor, and alert endpoints
"""

import requests
import json
import sys
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Generate unique test identifiers
test_id = int(time.time() * 1000) % 1000000

# Track test results
results = []
tokens = {}  # Store tokens for each user
users_to_cleanup = []

def log_test(test_num, description, passed, details=""):
    """Log test result in required format"""
    status = "[PASS]" if passed else "[FAIL]"
    results.append({
        "num": test_num,
        "description": description,
        "passed": passed,
        "status": status
    })
    print(f"{status} {description}")
    if details and not passed:
        print(f"       {details}")

def print_result(test_num, description, passed, details=""):
    """Print test result and log it"""
    log_test(test_num, description, passed, details)

# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

print("\n=== AUTHENTICATION TESTS ===\n")

# Test 1: Login Super Admin
try:
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": "dev", "password": "dev@123"}
    )
    passed = (
        response.status_code == 200 and
        "access_token" in response.json() and
        response.json().get("user", {}).get("role") == "admin" and
        response.json().get("user", {}).get("farm_ids") == []
    )
    tokens['dev'] = response.json().get("access_token") if response.status_code == 200 else None
    details = f"Status: {response.status_code}, Response: {response.json()}" if not passed else ""
    print_result(1, "Login Super Admin (dev)", passed, details)
except Exception as e:
    print_result(1, "Login Super Admin (dev)", False, str(e))

# Test 2: Login Admin
try:
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": "admin", "password": "Admin@123"}
    )
    passed = (
        response.status_code == 200 and
        "access_token" in response.json() and
        response.json().get("user", {}).get("role") == "admin" and
        len(response.json().get("user", {}).get("farm_ids", [])) > 0
    )
    tokens['admin'] = response.json().get("access_token") if response.status_code == 200 else None
    details = f"Status: {response.status_code}, Response: {response.json()}" if not passed else ""
    print_result(2, "Login Admin (admin)", passed, details)
except Exception as e:
    print_result(2, "Login Admin (admin)", False, str(e))

# Test 3: Login User
try:
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": "farmuser", "password": "User@123"}
    )
    passed = (
        response.status_code == 200 and
        "access_token" in response.json() and
        response.json().get("user", {}).get("role") == "user"
    )
    tokens['farmuser'] = response.json().get("access_token") if response.status_code == 200 else None
    details = f"Status: {response.status_code}, Response: {response.json()}" if not passed else ""
    print_result(3, "Login User (farmuser)", passed, details)
except Exception as e:
    print_result(3, "Login User (farmuser)", False, str(e))

# Test 4: Invalid login
try:
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": "fake", "password": "wrong"}
    )
    passed = response.status_code == 401
    details = f"Status: {response.status_code}, Expected: 401" if not passed else ""
    print_result(4, "Invalid login (fake credentials)", passed, details)
except Exception as e:
    print_result(4, "Invalid login (fake credentials)", False, str(e))

# Test 5: Empty credentials
try:
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": "", "password": ""}
    )
    passed = response.status_code in [401, 422]
    details = f"Status: {response.status_code}, Expected: 401 or 422" if not passed else ""
    print_result(5, "Empty credentials", passed, details)
except Exception as e:
    print_result(5, "Empty credentials", False, str(e))

# Test 6: No auth header
try:
    response = requests.get(f"{API_BASE}/auth/me")
    passed = response.status_code == 401
    details = f"Status: {response.status_code}, Expected: 401" if not passed else ""
    print_result(6, "GET /auth/me without auth header", passed, details)
except Exception as e:
    print_result(6, "GET /auth/me without auth header", False, str(e))

# Test 7: Bad token
try:
    response = requests.get(
        f"{API_BASE}/auth/me",
        headers={"Authorization": "Bearer invalidtoken123"}
    )
    passed = response.status_code == 401
    details = f"Status: {response.status_code}, Expected: 401" if not passed else ""
    print_result(7, "GET /auth/me with invalid token", passed, details)
except Exception as e:
    print_result(7, "GET /auth/me with invalid token", False, str(e))

# ============================================================================
# PROFILE TESTS (Tests 8-10)
# ============================================================================

print("\n=== PROFILE TESTS ===\n")

profile_tests = [
    (8, "dev", tokens.get('dev'), "dev", "admin"),
    (9, "admin", tokens.get('admin'), "admin", "admin"),
    (10, "farmuser", tokens.get('farmuser'), "farmuser", "user"),
]

for test_num, username, token, expected_username, expected_role in profile_tests:
    if not token:
        print_result(test_num, f"GET /auth/me ({username})", False, "No token available")
        continue
    try:
        response = requests.get(
            f"{API_BASE}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        # Response is user data directly, not wrapped in "user" key
        user = response.json() if response.status_code == 200 else {}
        passed = (
            response.status_code == 200 and
            user.get("username") == expected_username and
            user.get("role") == expected_role and
            "farm_ids" in user and
            "is_active" in user and
            "email" in user
        )
        details = f"Status: {response.status_code}, User: {user}" if not passed else ""
        print_result(test_num, f"GET /auth/me ({username}) - verify profile", passed, details)
    except Exception as e:
        print_result(test_num, f"GET /auth/me ({username}) - verify profile", False, str(e))

# ============================================================================
# USER MANAGEMENT TESTS (Super Admin)
# ============================================================================

print("\n=== USER MANAGEMENT TESTS (Super Admin) ===\n")

dev_token = tokens.get('dev')

# Test 11: GET /auth/users
try:
    response = requests.get(
        f"{API_BASE}/auth/users",
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code == 200 and isinstance(response.json(), list)
    details = f"Status: {response.status_code}, Response type: {type(response.json())}" if not passed else ""
    print_result(11, "GET /auth/users (super admin)", passed, details)
except Exception as e:
    print_result(11, "GET /auth/users (super admin)", False, str(e))

# Test 12: Create user
try:
    test_username = f"qatest{test_id}"
    response = requests.post(
        f"{API_BASE}/auth/register",
        json={
            "username": test_username,
            "email": f"qa{test_id}@test.com",
            "password": "QaTest@123",
            "full_name": "QA Test",
            "role": "user",
            "farm_ids": ["Farm-A"]
        },
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code == 200
    users_to_cleanup.append(test_username)
    details = f"Status: {response.status_code}, Response: {response.json()}" if not passed else ""
    print_result(12, "POST /auth/register (create user)", passed, details)
except Exception as e:
    print_result(12, "POST /auth/register (create user)", False, str(e))

# Test 13: Duplicate username
try:
    response = requests.post(
        f"{API_BASE}/auth/register",
        json={
            "username": test_username,
            "email": f"qa{test_id}b@test.com",
            "password": "QaTest@123",
            "full_name": "QA Test",
            "role": "user",
            "farm_ids": ["Farm-A"]
        },
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code in [400, 409]
    details = f"Status: {response.status_code}, Expected: 400 or 409" if not passed else ""
    print_result(13, "POST /auth/register (duplicate username)", passed, details)
except Exception as e:
    print_result(13, "POST /auth/register (duplicate username)", False, str(e))

# Test 14: Short password
try:
    response = requests.post(
        f"{API_BASE}/auth/register",
        json={
            "username": f"qatest{test_id}b",
            "email": f"qa{test_id}b@test.com",
            "password": "ab",
            "full_name": "QA Test",
            "role": "user",
            "farm_ids": ["Farm-A"]
        },
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code == 422
    details = f"Status: {response.status_code}, Expected: 422" if not passed else ""
    print_result(14, "POST /auth/register (short password)", passed, details)
except Exception as e:
    print_result(14, "POST /auth/register (short password)", False, str(e))

# Test 15: Invalid email
try:
    response = requests.post(
        f"{API_BASE}/auth/register",
        json={
            "username": f"qatest{test_id}c",
            "email": "notanemail",
            "password": "QaTest@123",
            "full_name": "QA Test",
            "role": "user",
            "farm_ids": ["Farm-A"]
        },
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code == 422
    details = f"Status: {response.status_code}, Expected: 422" if not passed else ""
    print_result(15, "POST /auth/register (invalid email)", passed, details)
except Exception as e:
    print_result(15, "POST /auth/register (invalid email)", False, str(e))

# Test 16: Update user
try:
    response = requests.put(
        f"{API_BASE}/auth/users/{test_username}",
        json={"full_name": "QA Updated"},
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code == 200
    details = f"Status: {response.status_code}, Response: {response.json()}" if not passed else ""
    print_result(16, f"PUT /auth/users/{test_username} (update user)", passed, details)
except Exception as e:
    print_result(16, f"PUT /auth/users/{test_username} (update user)", False, str(e))

# Test 17: Deactivate user
try:
    response = requests.delete(
        f"{API_BASE}/auth/users/{test_username}",
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code == 200
    users_to_cleanup.remove(test_username)  # Already cleaned up
    details = f"Status: {response.status_code}, Response: {response.json()}" if not passed else ""
    print_result(17, f"DELETE /auth/users/{test_username} (deactivate user)", passed, details)
except Exception as e:
    print_result(17, f"DELETE /auth/users/{test_username} (deactivate user)", False, str(e))

# ============================================================================
# USER MANAGEMENT TESTS (Admin token - scoped)
# ============================================================================

print("\n=== USER MANAGEMENT TESTS (Admin token) ===\n")

admin_token = tokens.get('admin')

# Test 18: GET /auth/users with admin token
try:
    response = requests.get(
        f"{API_BASE}/auth/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    passed = response.status_code == 200
    details = f"Status: {response.status_code}" if not passed else ""
    print_result(18, "GET /auth/users (admin token)", passed, details)
except Exception as e:
    print_result(18, "GET /auth/users (admin token)", False, str(e))

# Test 19: Create user with admin token
try:
    test_admin_user = f"qatest_admin{test_id}"
    response = requests.post(
        f"{API_BASE}/auth/register",
        json={
            "username": test_admin_user,
            "email": f"qa_admin{test_id}@test.com",
            "password": "QaTest@123",
            "full_name": "QA Admin Test",
            "role": "user",
            "farm_ids": ["Farm-A"]
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    passed = response.status_code == 200
    if passed:
        users_to_cleanup.append(test_admin_user)
    details = f"Status: {response.status_code}, Response: {response.json()}" if not passed else ""
    print_result(19, "POST /auth/register (admin can create user)", passed, details)
except Exception as e:
    print_result(19, "POST /auth/register (admin can create user)", False, str(e))

# ============================================================================
# USER MANAGEMENT TESTS (User token - restricted)
# ============================================================================

print("\n=== USER MANAGEMENT TESTS (User token - restricted) ===\n")

user_token = tokens.get('farmuser')

# Test 20: GET /auth/users with user token
try:
    response = requests.get(
        f"{API_BASE}/auth/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    # Should be 403 or return empty/restricted list
    passed = response.status_code in [403, 200]
    if response.status_code == 200:
        # If it returns 200, it should be empty or restricted
        data = response.json()
        passed = isinstance(data, list) and len(data) == 0
    details = f"Status: {response.status_code}" if not passed else ""
    print_result(20, "GET /auth/users (user token - restricted)", passed, details)
except Exception as e:
    print_result(20, "GET /auth/users (user token - restricted)", False, str(e))

# Test 21: POST /auth/register with user token
try:
    response = requests.post(
        f"{API_BASE}/auth/register",
        json={
            "username": "qatest_fail",
            "email": "qa_fail@test.com",
            "password": "QaTest@123",
            "full_name": "QA Fail Test",
            "role": "user",
            "farm_ids": ["Farm-A"]
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    passed = response.status_code == 403
    details = f"Status: {response.status_code}, Expected: 403" if not passed else ""
    print_result(21, "POST /auth/register (user token - restricted)", passed, details)
except Exception as e:
    print_result(21, "POST /auth/register (user token - restricted)", False, str(e))

# ============================================================================
# CATTLE TESTS
# ============================================================================

print("\n=== CATTLE TESTS ===\n")

cattle_id = None

# Test 22: GET /cattle (super admin)
try:
    response = requests.get(
        f"{API_BASE}/cattle",
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code == 200 and isinstance(response.json(), list)
    if passed and len(response.json()) > 0:
        cattle_id = response.json()[0].get("cid")
    details = f"Status: {response.status_code}" if not passed else ""
    print_result(22, "GET /cattle (super admin)", passed, details)
except Exception as e:
    print_result(22, "GET /cattle (super admin)", False, str(e))

# Test 23: GET /cattle/latest (super admin)
try:
    response = requests.get(
        f"{API_BASE}/cattle/latest",
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code == 200
    details = f"Status: {response.status_code}" if not passed else ""
    print_result(23, "GET /cattle/latest (super admin)", passed, details)
except Exception as e:
    print_result(23, "GET /cattle/latest (super admin)", False, str(e))

# Test 24: GET /cattle (admin token)
try:
    response = requests.get(
        f"{API_BASE}/cattle",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    passed = response.status_code == 200 and isinstance(response.json(), list)
    details = f"Status: {response.status_code}" if not passed else ""
    print_result(24, "GET /cattle (admin token)", passed, details)
except Exception as e:
    print_result(24, "GET /cattle (admin token)", False, str(e))

# Test 25: GET /cattle (user token)
try:
    response = requests.get(
        f"{API_BASE}/cattle",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    passed = response.status_code == 200 and isinstance(response.json(), list)
    details = f"Status: {response.status_code}" if not passed else ""
    print_result(25, "GET /cattle (user token)", passed, details)
except Exception as e:
    print_result(25, "GET /cattle (user token)", False, str(e))

# ============================================================================
# SENSOR/HEALTH DATA TESTS
# ============================================================================

print("\n=== SENSOR/HEALTH DATA TESTS ===\n")

if cattle_id:
    # Test 26: GET /cattle/{cid}/latest
    try:
        response = requests.get(
            f"{API_BASE}/cattle/{cattle_id}/latest",
            headers={"Authorization": f"Bearer {dev_token}"}
        )
        passed = response.status_code == 200
        details = f"Status: {response.status_code}" if not passed else ""
        print_result(26, f"GET /cattle/{cattle_id}/latest", passed, details)
    except Exception as e:
        print_result(26, f"GET /cattle/{cattle_id}/latest", False, str(e))

    # Test 27: GET /cattle/{cid}/last-hour (404 if no data is OK)
    try:
        response = requests.get(
            f"{API_BASE}/cattle/{cattle_id}/last-hour",
            headers={"Authorization": f"Bearer {dev_token}"}
        )
        # Accept 200 (has data) or 404 (no data, which is valid)
        passed = response.status_code in [200, 404]
        details = f"Status: {response.status_code}, Expected: 200 or 404" if not passed else ""
        print_result(27, f"GET /cattle/{cattle_id}/last-hour", passed, details)
    except Exception as e:
        print_result(27, f"GET /cattle/{cattle_id}/last-hour", False, str(e))

    # Test 28: GET /cattle/{cid}/health-events (404 if no data is OK)
    try:
        response = requests.get(
            f"{API_BASE}/cattle/{cattle_id}/health-events",
            headers={"Authorization": f"Bearer {dev_token}"}
        )
        # Accept 200 (has events) or 404 (no events, which is valid)
        passed = response.status_code in [200, 404]
        details = f"Status: {response.status_code}, Expected: 200 or 404" if not passed else ""
        print_result(28, f"GET /cattle/{cattle_id}/health-events", passed, details)
    except Exception as e:
        print_result(28, f"GET /cattle/{cattle_id}/health-events", False, str(e))
else:
    print_result(26, f"GET /cattle/{{cid}}/latest", False, "No cattle ID available")
    print_result(27, f"GET /cattle/{{cid}}/last-hour", False, "No cattle ID available")
    print_result(28, f"GET /cattle/{{cid}}/health-events", False, "No cattle ID available")

# ============================================================================
# ALERT TESTS
# ============================================================================

print("\n=== ALERT TESTS ===\n")

# Test 29: GET /alerts/recent/all (super admin)
try:
    response = requests.get(
        f"{API_BASE}/alerts/recent/all",
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code == 200
    details = f"Status: {response.status_code}" if not passed else ""
    print_result(29, "GET /alerts/recent/all (super admin)", passed, details)
except Exception as e:
    print_result(29, "GET /alerts/recent/all (super admin)", False, str(e))

# Test 30: POST /alerts/evaluate-all (super admin)
try:
    response = requests.post(
        f"{API_BASE}/alerts/evaluate-all",
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code == 200
    details = f"Status: {response.status_code}" if not passed else ""
    print_result(30, "POST /alerts/evaluate-all (super admin)", passed, details)
except Exception as e:
    print_result(30, "POST /alerts/evaluate-all (super admin)", False, str(e))

# ============================================================================
# EDGE CASES
# ============================================================================

print("\n=== EDGE CASES ===\n")

# Test 31: GET /cattle/99999/latest (non-existent)
try:
    response = requests.get(
        f"{API_BASE}/cattle/99999/latest",
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code in [404, 200]  # 404 or 200 with null data
    details = f"Status: {response.status_code}" if not passed else ""
    print_result(31, "GET /cattle/99999/latest (non-existent cattle)", passed, details)
except Exception as e:
    print_result(31, "GET /cattle/99999/latest (non-existent cattle)", False, str(e))

# Test 32: PUT /auth/users/nonexistent (non-existent user)
try:
    response = requests.put(
        f"{API_BASE}/auth/users/nonexistent",
        json={"full_name": "x"},
        headers={"Authorization": f"Bearer {dev_token}"}
    )
    passed = response.status_code == 404
    details = f"Status: {response.status_code}, Expected: 404" if not passed else ""
    print_result(32, "PUT /auth/users/nonexistent (non-existent user)", passed, details)
except Exception as e:
    print_result(32, "PUT /auth/users/nonexistent (non-existent user)", False, str(e))

# ============================================================================
# CLEANUP
# ============================================================================

print("\n=== CLEANUP ===\n")

for username in users_to_cleanup:
    try:
        response = requests.delete(
            f"{API_BASE}/auth/users/{username}",
            headers={"Authorization": f"Bearer {dev_token}"}
        )
        if response.status_code == 200:
            print(f"✓ Cleaned up user: {username}")
        else:
            print(f"✗ Failed to clean up user: {username} (Status: {response.status_code})")
    except Exception as e:
        print(f"✗ Error cleaning up user: {username} - {str(e)}")

# ============================================================================
# SUMMARY
# ============================================================================

passed_count = sum(1 for r in results if r["passed"])
total_count = len(results)
failed_count = total_count - passed_count

print("\n" + "="*60)
print(f"SUMMARY: {passed_count}/{total_count} passed, {failed_count} failed")
print("="*60)

# Exit with appropriate code
sys.exit(0 if failed_count == 0 else 1)
