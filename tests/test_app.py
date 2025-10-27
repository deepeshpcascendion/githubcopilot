import uuid
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def unique_email():
    return f"test-{uuid.uuid4().hex}@example.com"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity: Chess Club is one of the seeded activities
    assert "Chess Club" in data


def test_signup_and_unregister():
    email = unique_email()
    activity = "Chess Club"

    signup_url = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    r = client.post(signup_url)
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Confirm participant present
    r2 = client.get("/activities")
    participants = r2.json()[activity]["participants"]
    assert email in participants

    # Now unregister
    unregister_url = f"/activities/{quote(activity)}/unregister?email={quote(email)}"
    r3 = client.post(unregister_url)
    assert r3.status_code == 200

    r4 = client.get("/activities")
    assert email not in r4.json()[activity]["participants"]


def test_signup_duplicate():
    email = unique_email()
    activity = "Chess Club"
    signup_url = f"/activities/{quote(activity)}/signup?email={quote(email)}"

    r1 = client.post(signup_url)
    assert r1.status_code == 200

    # second signup should fail with 400
    r2 = client.post(signup_url)
    assert r2.status_code == 400
