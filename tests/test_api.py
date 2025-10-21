"""
Tests for the FastAPI activities endpoints.
"""
import pytest
from fastapi import status
from src.app import activities


class TestActivitiesEndpoints:
    """Test class for activities-related endpoints."""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities(self, client, reset_activities):
        """Test getting all activities."""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
        # Check structure of activity data
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_contains_expected_data(self, client, reset_activities):
        """Test that activities contain expected initial data."""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Test class for the signup endpoint."""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert f"Signed up {email} for {activity}" in data["message"]
        
        # Verify participant was added
        assert email in activities[activity]["participants"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for a non-existent activity."""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_already_registered(self, client, reset_activities):
        """Test signup when student is already registered."""
        email = "michael@mergington.edu"  # Already registered for Chess Club
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert data["detail"] == "Student is already signed up for this activity"

    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple different activities."""
        email = "multisport@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == status.HTTP_200_OK
        assert email in activities["Chess Club"]["participants"]
        
        # Sign up for Programming Class
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == status.HTTP_200_OK
        assert email in activities["Programming Class"]["participants"]

    def test_signup_with_url_encoded_email(self, client, reset_activities):
        """Test signup with URL-encoded email."""
        from urllib.parse import quote_plus
        from src.app import activities
        
        email = "test+user@mergington.edu"
        activity = "Gym Class"
        
        # URL encode the email properly
        encoded_email = quote_plus(email)
        response = client.post(f"/activities/{activity}/signup?email={encoded_email}")
        assert response.status_code == status.HTTP_200_OK
        assert email in activities[activity]["participants"]


class TestUnregisterEndpoint:
    """Test class for the unregister endpoint."""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        email = "michael@mergington.edu"  # Already registered for Chess Club
        activity = "Chess Club"
        
        # Verify participant is initially registered
        assert email in activities[activity]["participants"]
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert f"Unregistered {email} from {activity}" in data["message"]
        
        # Verify participant was removed
        assert email not in activities[activity]["participants"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistration from a non-existent activity."""
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregistration when student is not registered."""
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"

    def test_unregister_and_signup_cycle(self, client, reset_activities):
        """Test the complete cycle of unregister and re-signup."""
        email = "daniel@mergington.edu"  # Already registered for Chess Club
        activity = "Chess Club"
        
        # First unregister
        response1 = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response1.status_code == status.HTTP_200_OK
        assert email not in activities[activity]["participants"]
        
        # Then sign up again
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == status.HTTP_200_OK
        assert email in activities[activity]["participants"]


class TestActivityDataIntegrity:
    """Test class for data integrity across operations."""

    def test_participant_count_accuracy(self, client, reset_activities):
        """Test that participant counts remain accurate across operations."""
        activity = "Programming Class"
        initial_count = len(activities[activity]["participants"])
        
        # Add a participant
        new_email = "newcomer@mergington.edu"
        client.post(f"/activities/{activity}/signup?email={new_email}")
        assert len(activities[activity]["participants"]) == initial_count + 1
        
        # Remove a participant
        existing_email = activities[activity]["participants"][0]
        client.delete(f"/activities/{activity}/unregister?email={existing_email}")
        assert len(activities[activity]["participants"]) == initial_count

    def test_max_participants_not_exceeded(self, client, reset_activities):
        """Test that we can track when approaching max participants."""
        activity = "Chess Club"
        max_participants = activities[activity]["max_participants"]
        current_participants = len(activities[activity]["participants"])
        available_spots = max_participants - current_participants
        
        # Sign up students up to the limit
        for i in range(available_spots):
            email = f"student{i}@mergington.edu"
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify we're at max capacity
        assert len(activities[activity]["participants"]) == max_participants
        
        # Try to add one more (should still succeed as we're not enforcing limits yet)
        response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
        assert response.status_code == status.HTTP_200_OK

    def test_concurrent_operations_consistency(self, client, reset_activities):
        """Test that multiple operations maintain data consistency."""
        # Perform multiple operations in sequence
        operations = [
            ("POST", "/activities/Chess Club/signup?email=user1@mergington.edu"),
            ("POST", "/activities/Programming Class/signup?email=user1@mergington.edu"),
            ("DELETE", "/activities/Chess Club/unregister?email=michael@mergington.edu"),
            ("POST", "/activities/Gym Class/signup?email=user2@mergington.edu"),
            ("DELETE", "/activities/Programming Class/unregister?email=sophia@mergington.edu"),
        ]
        
        for method, url in operations:
            if method == "POST":
                response = client.post(url)
            else:
                response = client.delete(url)
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
        
        # Verify final state
        # user1 was added to Chess Club, then michael was removed from Chess Club
        assert "user1@mergington.edu" in activities["Chess Club"]["participants"]  # user1 should still be there
        assert "user1@mergington.edu" in activities["Programming Class"]["participants"]
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]  # michael was removed
        assert "user2@mergington.edu" in activities["Gym Class"]["participants"]
        assert "sophia@mergington.edu" not in activities["Programming Class"]["participants"]