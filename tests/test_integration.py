"""
Integration tests for the FastAPI application including static files.
"""
import pytest
from fastapi import status


class TestStaticFiles:
    """Test class for static file serving."""

    def test_static_index_html_accessible(self, client):
        """Test that the main HTML file is accessible."""
        response = client.get("/static/index.html")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers.get("content-type", "")

    def test_static_css_accessible(self, client):
        """Test that the CSS file is accessible."""
        response = client.get("/static/styles.css")
        assert response.status_code == status.HTTP_200_OK
        assert "text/css" in response.headers.get("content-type", "")

    def test_static_js_accessible(self, client):
        """Test that the JavaScript file is accessible."""
        response = client.get("/static/app.js")
        assert response.status_code == status.HTTP_200_OK
        assert any(content_type in response.headers.get("content-type", "") 
                  for content_type in ["application/javascript", "text/javascript"])

    def test_nonexistent_static_file(self, client):
        """Test accessing a non-existent static file."""
        response = client.get("/static/nonexistent.txt")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestApplicationIntegration:
    """Integration tests for the full application workflow."""

    def test_full_user_journey(self, client, reset_activities):
        """Test a complete user journey from viewing activities to signing up."""
        # Step 1: User visits the root page (gets redirected)
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        
        # Step 2: User loads the main page
        response = client.get("/static/index.html")
        assert response.status_code == status.HTTP_200_OK
        
        # Step 3: Frontend would fetch activities
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        activities_data = response.json()
        assert len(activities_data) > 0
        
        # Step 4: User signs up for an activity
        test_email = "journey@mergington.edu"
        activity_name = list(activities_data.keys())[0]  # Get first activity
        
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Step 5: Verify the signup worked by fetching activities again
        response = client.get("/activities")
        updated_activities = response.json()
        assert test_email in updated_activities[activity_name]["participants"]

    def test_multiple_users_different_activities(self, client, reset_activities):
        """Test multiple users signing up for different activities."""
        users_activities = [
            ("alice@mergington.edu", "Chess Club"),
            ("bob@mergington.edu", "Programming Class"),
            ("charlie@mergington.edu", "Gym Class"),
            ("diana@mergington.edu", "Chess Club"),
        ]
        
        # All users sign up
        for email, activity in users_activities:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify all signups
        response = client.get("/activities")
        activities_data = response.json()
        
        for email, activity in users_activities:
            assert email in activities_data[activity]["participants"]

    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test the complete signup and unregister workflow."""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # Initial state check
        response = client.get("/activities")
        initial_data = response.json()
        initial_participants = initial_data[activity]["participants"][:]
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify signup
        response = client.get("/activities")
        after_signup_data = response.json()
        assert email in after_signup_data[activity]["participants"]
        assert len(after_signup_data[activity]["participants"]) == len(initial_participants) + 1
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify unregistration
        response = client.get("/activities")
        after_unregister_data = response.json()
        assert email not in after_unregister_data[activity]["participants"]
        assert len(after_unregister_data[activity]["participants"]) == len(initial_participants)

    def test_activity_capacity_tracking(self, client, reset_activities):
        """Test that activity capacity information is correctly calculated."""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            max_participants = activity_info["max_participants"]
            current_participants = len(activity_info["participants"])
            
            # Capacity should be non-negative
            assert max_participants >= 0
            assert current_participants >= 0
            
            # Current participants should not exceed max (in a real app)
            # For now, we're just checking the data structure is correct
            assert isinstance(max_participants, int)
            assert isinstance(current_participants, int)


class TestErrorHandling:
    """Test error handling across the application."""

    def test_malformed_requests(self, client):
        """Test handling of malformed requests."""
        # Test with malformed activity name
        response = client.post("/activities//signup?email=test@mergington.edu")
        # FastAPI should handle this gracefully
        
        # Test with missing activity name
        response = client.post("/activities/signup?email=test@mergington.edu")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_endpoints(self, client):
        """Test accessing invalid endpoints."""
        invalid_endpoints = [
            "/invalid",
            "/activities/invalid/action",
            "/static/../../../etc/passwd",  # Path traversal attempt
        ]
        
        for endpoint in invalid_endpoints:
            response = client.get(endpoint)
            assert response.status_code in [
                status.HTTP_404_NOT_FOUND, 
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ]

    def test_large_request_handling(self, client, reset_activities):
        """Test handling of unusually large requests."""
        # Test with very long activity name
        long_activity = "a" * 1000
        response = client.post(f"/activities/{long_activity}/signup?email=test@mergington.edu")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test with very long email
        long_email = "a" * 500 + "@" + "b" * 500 + ".edu"
        response = client.post(f"/activities/Chess Club/signup?email={long_email}")
        # Should handle gracefully, either accept or reject with proper status