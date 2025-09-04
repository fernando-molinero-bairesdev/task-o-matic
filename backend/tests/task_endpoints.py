import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid
from constants import Status, Priority

class TestTaskEndpoints:
    """Test suite for task management endpoints."""

    def test_get_task_statuses(self, client):
        """Test getting available task statuses."""
        response = client.get("/tasks/statuses")
        
        assert response.status_code == 200
        data = response.json()
        assert "TO_DO" in data
        assert "IN_PROGRESS" in data
        assert "DONE" in data
        assert data["TO_DO"] == Status.TO_DO
        assert data["IN_PROGRESS"] == Status.IN_PROGRESS
        assert data["DONE"] == Status.DONE

    def test_create_task_success(self, client, auth_headers):
        """Test successful task creation."""
        task_data = {
            "title": "New Test Task",
            "description": "A new test task description",
            "status": Status.TO_DO,
            "priority": 1,
            "due_date": (datetime.utcnow() + timedelta(days=5)).isoformat(),
            "tags": ["urgent", "testing"]
        }
        
        response = client.post("/tasks/", json=task_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["status"] == task_data["status"]
        assert data["priority"] == task_data["priority"]
        assert data["tags"] == task_data["tags"]
        assert "task_uuid" in data

    def test_create_task_missing_title(self, client, auth_headers):
        """Test task creation with missing title."""
        task_data = {
            "description": "Task without title",
            "status": Status.TO_DO,
            "priority": 2
        }
        
        response = client.post("/tasks/", json=task_data, headers=auth_headers)
        assert response.status_code == 422

    def test_create_task_unauthorized(self, client):
        """Test task creation without authentication."""
        task_data = {
            "title": "Unauthorized Task",
            "description": "Should fail",
            "status": Status.TO_DO,
            "priority": 2
        }
        
        response = client.post("/tasks/", json=task_data)
        assert response.status_code == 401

    def test_get_tasks_success(self, client, auth_headers, test_task):
        """Test getting tasks list."""
        response = client.get("/tasks/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check if our test task is in the response
        task_titles = [task["title"] for task in data]
        assert test_task.title in task_titles

    def test_get_tasks_with_filters(self, client, auth_headers, test_task):
        """Test getting tasks with filters."""
        # Test status filter
        response = client.get(f"/tasks/?status={Status.TO_DO}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        for task in data:
            assert task["status"] == Status.TO_DO

        # Test pagination
        response = client.get("/tasks/?skip=0&limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_get_task_by_id_success(self, client, auth_headers, test_task):
        """Test getting a specific task by ID."""
        response = client.get(f"/tasks/{test_task.task_uuid}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_uuid"] == str(test_task.task_uuid)
        assert data["title"] == test_task.title
        assert data["description"] == test_task.description

    def test_get_task_by_id_not_found(self, client, auth_headers):
        """Test getting a non-existent task."""
        fake_uuid = str(uuid.uuid4())
        response = client.get(f"/tasks/{fake_uuid}", headers=auth_headers)
        
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]

    def test_update_task_success(self, client, auth_headers, test_task):
        """Test successful task update."""
        update_data = {
            "title": "Updated Task Title",
            "description": "Updated description",
            "status": Status.IN_PROGRESS,
            "priority": 1
        }
        
        response = client.put(
            f"/tasks/{test_task.task_uuid}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["status"] == update_data["status"]
        assert data["priority"] == update_data["priority"]

    def test_update_task_partial(self, client, auth_headers, test_task):
        """Test partial task update."""
        update_data = {
            "title": "Partially Updated Task"
        }
        
        response = client.put(
            f"/tasks/{test_task.task_uuid}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        # Original description should remain unchanged
        assert data["description"] == test_task.description

    def test_update_task_not_found(self, client, auth_headers):
        """Test updating a non-existent task."""
        fake_uuid = str(uuid.uuid4())
        update_data = {"title": "Updated Title"}
        
        response = client.put(
            f"/tasks/{fake_uuid}", 
            json=update_data, 
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_delete_task_success(self, client, auth_headers, test_task):
        """Test successful task deletion (soft delete)."""
        response = client.delete(f"/tasks/{test_task.task_uuid}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_uuid"] == str(test_task.task_uuid)
        
        # Verify task is soft deleted (should not appear in GET requests)
        get_response = client.get(f"/tasks/{test_task.task_uuid}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client, auth_headers):
        """Test deleting a non-existent task."""
        fake_uuid = str(uuid.uuid4())
        response = client.delete(f"/tasks/{fake_uuid}", headers=auth_headers)
        
        assert response.status_code == 404

    def test_assign_task_success(self, client, auth_headers, test_task, test_user2):
        """Test successful task assignment."""
        assignment_data = {
            "user_uuid": str(test_user2.user_uuid)
        }
        
        response = client.post(
            f"/tasks/{test_task.task_uuid}/assign",
            json=assignment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["assigned_to"] == str(test_user2.user_uuid)

    def test_assign_task_to_nonexistent_user(self, client, auth_headers, test_task):
        """Test assigning task to non-existent user."""
        fake_user_uuid = str(uuid.uuid4())
        assignment_data = {
            "user_uuid": fake_user_uuid
        }
        
        response = client.post(
            f"/tasks/{test_task.task_uuid}/assign",
            json=assignment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_unassign_task_success(self, client, auth_headers, test_task, test_user2):
        """Test successful task unassignment."""
        # First assign the task
        assignment_data = {"user_uuid": str(test_user2.user_uuid)}
        assign_response = client.post(
            f"/tasks/{test_task.task_uuid}/assign",
            json=assignment_data,
            headers=auth_headers
        )
        assert assign_response.status_code == 200
        
        # Then unassign the task
        unassignment_data = {"user_uuid": None}
        response = client.post(
            f"/tasks/{test_task.task_uuid}/assign",
            json=unassignment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["assigned_to"] is None

    def test_assign_task_not_found(self, client, auth_headers, test_user2):
        """Test assigning a non-existent task."""
        fake_uuid = str(uuid.uuid4())
        assignment_data = {
            "user_uuid": str(test_user2.user_uuid)
        }
        
        response = client.post(
            f"/tasks/{fake_uuid}/assign",
            json=assignment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404

    def test_complete_task_success(self, client, auth_headers, test_task):
        """Test successful task completion."""
        response = client.post(
            f"/tasks/{test_task.task_uuid}/complete",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == Status.DONE
        assert data["completed_date"] is not None

    def test_complete_task_not_found(self, client, auth_headers):
        """Test completing a non-existent task."""
        fake_uuid = str(uuid.uuid4())
        response = client.post(f"/tasks/{fake_uuid}/complete", headers=auth_headers)
        
        assert response.status_code == 404

    def test_complete_already_completed_task(self, client, auth_headers, test_task):
        """Test completing an already completed task."""
        # First complete the task
        complete_response = client.post(
            f"/tasks/{test_task.task_uuid}/complete",
            headers=auth_headers
        )
        assert complete_response.status_code == 200
        
        # Try to complete it again
        response = client.post(
            f"/tasks/{test_task.task_uuid}/complete",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == Status.DONE

    def test_unauthorized_access_to_all_endpoints(self, client, test_task):
        """Test that all endpoints require authentication."""
        endpoints = [
            ("GET", f"/tasks/"),
            ("POST", f"/tasks/"),
            ("GET", f"/tasks/{test_task.task_uuid}"),
            ("PUT", f"/tasks/{test_task.task_uuid}"),
            ("DELETE", f"/tasks/{test_task.task_uuid}"),
            ("POST", f"/tasks/{test_task.task_uuid}/assign"),
            ("POST", f"/tasks/{test_task.task_uuid}/complete"),
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            assert response.status_code == 401, f"Endpoint {method} {endpoint} should require authentication"