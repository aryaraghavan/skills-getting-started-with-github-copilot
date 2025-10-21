"""
Tests for edge cases and error handling in the FastAPI application.
"""
import pytest
from fastapi import status
from urllib.parse import quote


class TestEdgeCases:
    """Test class for edge cases and error handling."""

    def test_activity_name_with_spaces_encoded(self, client, reset_activities):
        """Test activities with spaces in names are properly URL encoded."""
        activity = "Chess Club"  # Contains space
        email = "test@mergington.edu"
        
        # Test signup with URL encoding
        encoded_activity = quote(activity)
        response = client.post(f"/activities/{encoded_activity}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK

    def test_activity_name_with_special_characters(self, client, reset_activities):
        """Test handling of activity names with special characters."""
        # Add an activity with special characters for testing
        from src.app import activities
        special_activity = "Art & Design Class"
        activities[special_activity] = {
            "description": "Creative arts and design",
            "schedule": "Mondays, 2:00 PM - 4:00 PM",
            "max_participants": 15,
            "participants": []
        }
        
        email = "artist@mergington.edu"
        encoded_activity = quote(special_activity)
        
        response = client.post(f"/activities/{encoded_activity}/signup?email={email}")
        assert response.status_code == status.HTTP_200_OK

    def test_email_validation_edge_cases(self, client, reset_activities):
        """Test various email formats."""
        from src.app import activities
        
        activity = "Chess Club"
        
        # Test various valid email formats
        valid_emails = [
            "test@mergington.edu",
            "test.user@mergington.edu",
            "test+tag@mergington.edu",
            "test_user@mergington.edu",
            "123@mergington.edu"
        ]
        
        for email in valid_emails:
            # First unregister any existing participant to avoid conflicts
            existing_participants = list(activities[activity]["participants"])
            for participant in existing_participants:
                client.delete(f"/activities/{activity}/unregister?email={participant}")
            
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == status.HTTP_200_OK, f"Failed for email: {email}"

    def test_empty_email_parameter(self, client, reset_activities):
        """Test handling of empty email parameter."""
        activity = "Chess Club"
        
        # Test with empty email
        response = client.post(f"/activities/{activity}/signup?email=")
        # The API should handle this gracefully, depending on FastAPI's parameter validation

    def test_missing_email_parameter(self, client, reset_activities):
        """Test handling of missing email parameter."""
        activity = "Chess Club"
        
        # Test without email parameter
        response = client.post(f"/activities/{activity}/signup")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_case_sensitivity_activity_names(self, client, reset_activities):
        """Test case sensitivity in activity names."""
        email = "test@mergington.edu"
        
        # Test with different cases
        response1 = client.post(f"/activities/chess club/signup?email={email}")
        assert response1.status_code == status.HTTP_404_NOT_FOUND
        
        response2 = client.post(f"/activities/CHESS CLUB/signup?email={email}")
        assert response2.status_code == status.HTTP_404_NOT_FOUND
        
        # Only exact case should work
        response3 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response3.status_code == status.HTTP_200_OK

    def test_long_email_addresses(self, client, reset_activities):
        """Test handling of very long email addresses."""
        activity = "Gym Class"
        long_email = "a" * 50 + "@" + "b" * 50 + ".edu"
        
        response = client.post(f"/activities/{activity}/signup?email={long_email}")
        assert response.status_code == status.HTTP_200_OK

    def test_unicode_characters_in_email(self, client, reset_activities):
        """Test handling of unicode characters in email."""
        activity = "Programming Class"
        unicode_email = "tëst@mërgington.edu"
        
        response = client.post(f"/activities/{activity}/signup?email={unicode_email}")
        # Should handle unicode gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]


class TestDataConsistency:
    """Test class for data consistency and state management."""

    def test_activities_structure_preserved(self, client, reset_activities):
        """Test that the activities data structure is preserved across operations."""
        from src.app import activities
        
        # Store initial structure
        initial_keys = set(activities.keys())
        
        # Perform various operations
        client.post("/activities/Chess Club/signup?email=test1@mergington.edu")
        client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        client.post("/activities/Programming Class/signup?email=test2@mergington.edu")
        
        # Verify structure is preserved
        final_keys = set(activities.keys())
        assert initial_keys == final_keys
        
        # Verify each activity still has required fields
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_participant_list_integrity(self, client, reset_activities):
        """Test that participant lists maintain integrity."""
        from src.app import activities
        activity = "Chess Club"
        initial_participants = list(activities[activity]["participants"])
        
        # Add and remove participants multiple times
        test_emails = [
            "test1@mergington.edu",
            "test2@mergington.edu", 
            "test3@mergington.edu"
        ]
        
        for email in test_emails:
            client.post(f"/activities/{activity}/signup?email={email}")
            
        for email in test_emails:
            client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Should be back to initial state
        final_participants = activities[activity]["participants"]
        assert set(final_participants) == set(initial_participants)

    def test_no_duplicate_participants(self, client, reset_activities):
        """Test that no duplicate participants can exist."""
        from src.app import activities
        activity = "Programming Class"
        email = "duplicate@mergington.edu"
        
        # Sign up twice
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == status.HTTP_200_OK
        
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verify only one instance exists
        participant_count = activities[activity]["participants"].count(email)
        assert participant_count == 1


class TestHttpMethods:
    """Test class for HTTP method validation."""

    def test_signup_only_accepts_post(self, client, reset_activities):
        """Test that signup endpoint only accepts POST requests."""
        activity = "Chess Club"
        email = "test@mergington.edu"
        url = f"/activities/{activity}/signup?email={email}"
        
        # POST should work
        response_post = client.post(url)
        assert response_post.status_code == status.HTTP_200_OK
        
        # Other methods should not work
        response_get = client.get(url)
        assert response_get.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        response_put = client.put(url)
        assert response_put.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        response_patch = client.patch(url)
        assert response_patch.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_unregister_only_accepts_delete(self, client, reset_activities):
        """Test that unregister endpoint only accepts DELETE requests."""
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        url = f"/activities/{activity}/unregister?email={email}"
        
        # DELETE should work
        response_delete = client.delete(url)
        assert response_delete.status_code == status.HTTP_200_OK
        
        # Other methods should not work
        response_get = client.get(url)
        assert response_get.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        response_post = client.post(url)
        assert response_post.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        response_put = client.put(url)
        assert response_put.status_code == status.HTTP_405_METHOD_NOT_ALLOWED