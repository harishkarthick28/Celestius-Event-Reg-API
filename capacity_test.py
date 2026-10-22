
import json
import sqlite3
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE_URL = "http://127.0.0.1:8000"
TEST_PREFIX = "capacitytest-"


def request_api(path, method="GET", data=None):
    body = None if data is None else json.dumps(data).encode("utf-8")

    request = Request(
        BASE_URL + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urlopen(request) as response:
            return response.status, json.loads(response.read())

    except HTTPError as error:
        return error.code, json.loads(error.read())


def cleanup_test_records():
    connection = sqlite3.connect("registrations.db")
    connection.execute(
        "DELETE FROM registrations WHERE email LIKE ?",
        (TEST_PREFIX + "%",)
    )
    connection.commit()
    connection.close()


try:
    # Remove leftovers from an earlier run of this test only.
    cleanup_test_records()

    status, result = request_api("/registrations")
    assert status == 200, f"Could not list registrations: {result}"

    current = result["total_registrations"]
    capacity = result["capacity"]

    if current > capacity:
        raise RuntimeError("Existing registrations exceed capacity.")

    print(f"Starting registrations: {current}/{capacity}")

    # Fill every remaining seat using unique test emails.
    for number in range(1, capacity - current + 1):
        payload = {
            "name": f"Capacity Test {number}",
            "email": f"{TEST_PREFIX}{number:03d}@example.com",
            "college_department": "Testing"
        }

        status, result = request_api("/register", "POST", payload)

        if status != 201:
            raise RuntimeError(
                f"Registration {number} failed: {status} {result}"
            )

    status, result = request_api("/registrations")
    assert status == 200, result
    assert result["total_registrations"] == capacity, result

    print(f"Capacity reached: {capacity}/{capacity}")

    # Attempt one more registration.
    overflow_payload = {
        "name": "Overflow Test",
        "email": f"{TEST_PREFIX}overflow@example.com",
        "college_department": "Testing"
    }

    status, result = request_api(
        "/register", "POST", overflow_payload
    )

    if status == 409 and result.get("detail") == "Event is full.":
        print("PASS: The next registration was rejected.")
    else:
        print(f"FAIL: Expected 409 Event is full, got {status}: {result}")

finally:
    cleanup_test_records()
    print("Test registrations cleaned up.")
