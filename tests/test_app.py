"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and regional competitions",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["jessica@mergington.edu", "james@mergington.edu"]
        },
        "Music Band": {
            "description": "Play instruments and perform in concerts and school events",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills through competitive debate",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["andrew@mergington.edu", "rachel@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific experiments and participate in science fairs",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["tyler@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original_activities)
    yield
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


def test_root_redirect():
    """Test that root redirects to static/index.html"""
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200


def test_get_activities(reset_activities):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Basketball Team" in data
    assert len(data) == 9
    
    # Verify activity structure
    chess = data["Chess Club"]
    assert chess["description"] == "Learn strategies and compete in chess tournaments"
    assert chess["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert chess["max_participants"] == 12
    assert "michael@mergington.edu" in chess["participants"]


def test_signup_for_activity(reset_activities):
    """Test signing up a student for an activity"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "newstudent@mergington.edu" in data["message"]
    
    # Verify the student was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]


def test_signup_duplicate_email(reset_activities):
    """Test that duplicate signups are rejected"""
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael@mergington.edu"
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(reset_activities):
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_signoff_from_activity(reset_activities):
    """Test removing a student from an activity"""
    response = client.post(
        "/activities/Chess%20Club/signoff?email=michael@mergington.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Removed" in data["message"]
    assert "michael@mergington.edu" in data["message"]
    
    # Verify the student was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]


def test_signoff_not_registered(reset_activities):
    """Test removing a student who is not registered"""
    response = client.post(
        "/activities/Chess%20Club/signoff?email=notregistered@mergington.edu"
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_signoff_nonexistent_activity(reset_activities):
    """Test removing from a non-existent activity"""
    response = client.post(
        "/activities/Nonexistent%20Activity/signoff?email=test@mergington.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_multiple_signups_and_signoffs(reset_activities):
    """Test multiple signup and signoff operations"""
    # Sign up a new student
    response1 = client.post(
        "/activities/Basketball%20Team/signup?email=newplayer@mergington.edu"
    )
    assert response1.status_code == 200
    
    # Verify they're signed up
    activities_response = client.get("/activities")
    assert "newplayer@mergington.edu" in activities_response.json()["Basketball Team"]["participants"]
    
    # Sign them off
    response2 = client.post(
        "/activities/Basketball%20Team/signoff?email=newplayer@mergington.edu"
    )
    assert response2.status_code == 200
    
    # Verify they're removed
    activities_response = client.get("/activities")
    assert "newplayer@mergington.edu" not in activities_response.json()["Basketball Team"]["participants"]


def test_signup_multiple_activities(reset_activities):
    """Test a student signing up for multiple activities"""
    student_email = "multiactivity@mergington.edu"
    
    # Sign up for Chess Club
    response1 = client.post(
        "/activities/Chess%20Club/signup?email=" + student_email
    )
    assert response1.status_code == 200
    
    # Sign up for Basketball Team
    response2 = client.post(
        "/activities/Basketball%20Team/signup?email=" + student_email
    )
    assert response2.status_code == 200
    
    # Verify student is in both activities
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert student_email in activities_data["Chess Club"]["participants"]
    assert student_email in activities_data["Basketball Team"]["participants"]
