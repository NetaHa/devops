from fastapi.testclient import TestClient
from ex3_3.ex3.main import app, get_db_connection
from datetime import datetime, timezone, timedelta
import pytest

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM events")  # Clear the table before each test
    db.commit()
    yield db
    db.close()


def test_process_event(test_db):
    response = client.post("/process_event/", json={"userid": "user123", "eventname": "Test Event"})
    assert response.status_code == 200
    assert response.json() == {"message": "Event processed successfully"}

    cursor = test_db.cursor()
    cursor.execute("SELECT * FROM events")
    event_records = cursor.fetchall()
    assert len(event_records) == 1
    assert event_records[0][1] == "user123"
    assert event_records[0][2] == "Test Event"


def test_get_reports(test_db):
    # Insert a test event directly into the DB
    cursor = test_db.cursor()
    eventtimestamputc = datetime.now(timezone.utc) - timedelta(seconds=100)  # 100 seconds ago
    cursor.execute('''
    INSERT INTO events (eventtimestamputc, userid, eventname) VALUES (?, ?, ?)
    ''', (eventtimestamputc, 'user123', 'Test Event'))
    test_db.commit()

    # Test the /get_reports/ endpoint
    response = client.post("/get_reports/", params={"lastseconds": 200, "userid": "user123"})
    assert response.status_code == 200
    response_json = response.json()
    assert "events" in response_json
    assert len(response_json["events"]) == 1
    assert response_json["events"][0]["userid"] == "user123"
    assert response_json["events"][0]["eventname"] == "Test Event"

    # Check if an event outside the time range is not returned
    response = client.post("/get_reports/", params={"lastseconds": 50, "userid": "user123"})
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json["events"]) == 0  # No events should be returned
