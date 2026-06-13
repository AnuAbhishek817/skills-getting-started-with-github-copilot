"""
Test suite for activity endpoints using the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from urllib.parse import quote


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Set up the test client
        Act: Send GET request to /activities
        Assert: Verify response status and content
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Swimming Club",
            "Art Studio",
            "Drama Club",
            "Science Club",
            "Debate Team",
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == len(expected_activities)
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_returns_activity_details(self, client, existing_activity):
        """
        Arrange: Set up expected activity structure
        Act: Send GET request and extract activity
        Assert: Verify activity has required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()
        activity = activities[existing_activity]

        # Assert
        assert isinstance(activity, dict)
        assert all(field in activity for field in required_fields)
        assert isinstance(activity["participants"], list)
        assert isinstance(activity["max_participants"], int)

    def test_get_activities_participants_are_populated(self, client, existing_activity):
        """
        Arrange: Set up test to check existing participants
        Act: Fetch activities and retrieve participants
        Assert: Verify participants list is not empty
        """
        # Arrange
        expected_min_participants = 2

        # Act
        response = client.get("/activities")
        activities = response.json()
        participants = activities[existing_activity]["participants"]

        # Assert
        assert len(participants) >= expected_min_participants


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_for_activity_success(self, client, existing_activity, sample_email):
        """
        Arrange: Prepare test data with valid activity and email
        Act: Submit signup request
        Assert: Verify success response and participant added
        """
        # Arrange
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[existing_activity]["participants"].copy()

        # Act
        response = client.post(
            f"/activities/{existing_activity}/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]

        # Verify participant was added
        final_response = client.get("/activities")
        final_participants = final_response.json()[existing_activity]["participants"]
        assert sample_email in final_participants
        assert len(final_participants) == len(initial_participants) + 1

    def test_signup_for_nonexistent_activity(self, client, sample_email, nonexistent_activity):
        """
        Arrange: Set up request with nonexistent activity
        Act: Submit signup request
        Assert: Verify 404 error response
        """
        # Arrange
        expected_status = 404
        expected_detail = "Activity not found"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={sample_email}"
        )

        # Assert
        assert response.status_code == expected_status
        data = response.json()
        assert expected_detail in data["detail"]

    def test_signup_already_registered(self, client, existing_activity):
        """
        Arrange: Set up with already registered participant
        Act: Attempt to signup same participant again
        Assert: Verify 400 error for duplicate signup
        """
        # Arrange
        initial_response = client.get("/activities")
        existing_participant = initial_response.json()[existing_activity]["participants"][0]
        expected_status = 400

        # Act
        response = client.post(
            f"/activities/{existing_activity}/signup?email={existing_participant}"
        )

        # Assert
        assert response.status_code == expected_status
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_with_email_formatting(self, client, existing_activity):
        """
        Arrange: Set up test with special characters in email
        Act: Submit signup with special email format
        Assert: Verify signup works with URL encoding
        """
        # Arrange
        special_email = "test+student@mergington.edu"
        encoded_email = quote(special_email, safe='')

        # Act
        response = client.post(
            f"/activities/{existing_activity}/signup?email={encoded_email}"
        )

        # Assert
        assert response.status_code == 200
        final_response = client.get("/activities")
        participants = final_response.json()[existing_activity]["participants"]
        assert special_email in participants

    def test_signup_response_structure(self, client, existing_activity):
        """
        Arrange: Prepare test for response validation
        Act: Send signup request with new email
        Assert: Verify response has correct structure
        """
        # Arrange
        test_email = "response_test@mergington.edu"
        expected_keys = {"message"}

        # Act
        response = client.post(
            f"/activities/{existing_activity}/signup?email={test_email}"
        )
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert all(key in data for key in expected_keys)
        assert isinstance(data["message"], str)
