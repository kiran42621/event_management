import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from faker import Faker

from app.main import services

import string
import random

client = TestClient(services)
fake = Faker()

# Funcion which generates random string
def generate_random_string(length):
  characters = string.ascii_letters + string.digits  
  random_string = ''.join(random.choice(characters) for i in range(length))
  return random_string

def valid_event_payload(name="Test Event"):
  now = datetime.now(timezone.utc)
  return {
      "name": name,
      "location": "Bengaluru",
      "startTime": (now + timedelta(hours=1)).isoformat(),
      "endTime": (now + timedelta(hours=2)).isoformat(),
      "maxCapacity": 10
  }

def valid_attendee_payload(name="John Doe", email="john@example.com"):
  return {
    "name": name,
    "email": email
  }

def test_create_event_success():
  name = generate_random_string(10)
  response = client.post("/events", json=valid_event_payload(name))
  assert response.status_code == 200
  data = response.json()
  assert data["name"] == name
  assert "startTime" in data and "endTime" in data
  assert data["maxCapacity"] == 10

def test_create_event_start_after_end():
  now = datetime.now(timezone.utc)
  payload = valid_event_payload()
  payload["startTime"] = (now + timedelta(hours=3)).isoformat()
  payload["endTime"] = (now + timedelta(hours=2)).isoformat()
  response = client.post("/events", json=payload)
  assert response.status_code == 400
  assert "Invalid date" in response.text

def test_create_event_start_in_past():
  now = datetime.now(timezone.utc)
  payload = valid_event_payload()
  payload["startTime"] = (now - timedelta(hours=1)).isoformat()
  payload["endTime"] = (now + timedelta(hours=2)).isoformat()
  response = client.post("/events", json=payload)
  assert response.status_code == 400
  assert "Invalid date" in response.text

def test_create_event_invalid_capacity():
  payload = valid_event_payload()
  payload["maxCapacity"] = 0
  response = client.post("/events", json=payload)
  assert response.status_code == 400
  assert "Maximum capacity should be more than 0" in response.text

def test_create_event_duplicate_name():
  name = generate_random_string(10)
  payload = valid_event_payload(name)
  response1 = client.post("/events", json=payload)
  assert response1.status_code == 200
  
  response2 = client.post("/events", json=payload)
  assert response2.status_code == 400
  assert "Event name already exists" in response2.text


def test_get_event_success():
  name = generate_random_string(10)

  for i in range(3):
    payload = valid_event_payload(name=f"{name} {i}")
    response = client.post("/events", json=payload)
    assert response.status_code == 200

  response = client.get("/events?page=1")
  assert response.status_code == 200
  data = response.json()
  assert isinstance(data, list)
  assert len(data) > 0
  assert all("name" in ev for ev in data)

def test_get_event_invalid_page():
  response = client.get("/events?page=0")
  assert response.status_code == 400
  assert "Page cannot be negative or zero" in response.text

def test_get_event_no_events_found():
  response = client.get("/events?page=100")
  assert response.status_code == 400
  assert "No events found" in response.text

def test_register_attendee_success():
  name = generate_random_string(10)
  event_res = client.post("/events", json=valid_event_payload(name))
  assert event_res.status_code == 200
  event = event_res.json()

  attendee_payload = valid_attendee_payload(name=fake.name(), email=fake.email())
  register_res = client.post(f"/events/{event['id']}/register", json=attendee_payload)
  assert register_res.status_code == 200
  data = register_res.json()
  assert data["id"] == event["id"]

def test_register_attendee_invalid_event_id():
  attendee_payload = valid_attendee_payload(name=fake.name(), email=fake.email())
  response = client.post("/events/invalid-id/register", json=attendee_payload)
  assert response.status_code == 400
  assert "Invalid event id" in response.text

def test_register_attendee_event_not_found():
  fake_event_id = generate_random_string(10)
  attendee_payload = valid_attendee_payload(name=fake.name(), email=fake.email())
  response = client.post(f"/events/{fake_event_id}/register", json=attendee_payload)
  assert response.status_code == 400
  assert "Invalid event id" in response.text

def test_register_attendee_event_capacity_full():
  name = generate_random_string(10)
  event_res = client.post("/events", json=valid_event_payload(name))
  event = event_res.json()
  payload1 = valid_attendee_payload(name=fake.name(), email=fake.email())
  res1 = client.post(f"/events/{event['id']}/register", json=payload1)
  assert res1.status_code == 200
  for _ in range(10):
    payload2 = valid_attendee_payload(name=fake.name(), email=fake.email())
    res2 = client.post(f"/events/{event['id']}/register", json=payload2)
  payload2 = valid_attendee_payload(name=fake.name(), email=fake.email())
  res2 = client.post(f"/events/{event['id']}/register", json=payload2)
  assert res2.status_code == 400
  assert "slots are full" in res2.text

def test_register_attendee_already_registered():
  name = generate_random_string(10)
  event_res = client.post("/events", json=valid_event_payload(name))
  event = event_res.json()
  attendee = valid_attendee_payload(name=fake.name(), email=fake.email())
  res1 = client.post(f"/events/{event['id']}/register", json=attendee)
  assert res1.status_code == 200
  
  res2 = client.post(f"/events/{event['id']}/register", json=attendee)
  assert res2.status_code == 200

def test_get_attendees_success():
  name = generate_random_string(10)
  event_res = client.post("/events", json=valid_event_payload(name))
  assert event_res.status_code == 200
  event = event_res.json()

  attendee = valid_attendee_payload(name=fake.name(), email=fake.email())
  register_res = client.post(f"/events/{event['id']}/register", json=attendee)
  assert register_res.status_code == 200

  get_res = client.get(f"/events/{event['id']}/attendees")
  assert get_res.status_code == 200
  data = get_res.json()
  assert data["id"] == event["id"]
  assert "attendees" in data
  assert isinstance(data["attendees"], list)
  assert any(a["email"] == attendee["email"] for a in data["attendees"])

def test_get_attendees_invalid_event_id():
  response = client.get("/events//attendees")
  assert response.status_code in (404, 422)

def test_get_attendees_event_not_found():
  fake_event_id = generate_random_string(10)
  response = client.get(f"/events/{fake_event_id}/attendees")
  assert response.status_code == 400
  assert "Invalid event id" in response.text
