import pytest
from datetime import datetime, timedelta
from constants import Status

class TestTaskIntegration:
    """Integration tests for task workflows."""

    def test_complete_task_workflow(self, client, auth_headers):
        """Test complete workflow: create -> assign -> update -> complete -> delete."""
        # 1. Create task
        task_data = {
            "title": "Workflow Test Task",
            "description": "Testing complete workflow",
            "status": Status.TO_DO,
            "priority": 2,
            "due_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),
            "tags": ["workflow", "test"]
        }
        
        create_response = client.post("/tasks/", json=task_data, headers=auth_headers)
        assert create_response.status_code == 200
        task = create_response.json()
        task_uuid = task["task_uuid"]

        # 2. Update task status
        update_data = {"status": Status.IN_PROGRESS}
        update_response = client.put(f"/tasks/{task_uuid}", json=update_data, headers=auth_headers)
        assert update_response.status_code == 200
        assert update_response.json()["status"] == Status.IN_PROGRESS

        # 3. Complete task
        complete_response = client.post(f"/tasks/{task_uuid}/complete", headers=auth_headers)
        assert complete_response.status_code == 200
        completed_task = complete_response.json()
        assert completed_task["status"] == Status.DONE
        assert completed_task["completed_date"] is not None

        # 4. Verify task appears in filtered results
        done_tasks_response = client.get(f"/tasks/?status={Status.DONE}", headers=auth_headers)
        assert done_tasks_response.status_code == 200
        done_tasks = done_tasks_response.json()
        task_uuids = [t["task_uuid"] for t in done_tasks]
        assert task_uuid in task_uuids

        # 5. Soft delete task
        delete_response = client.delete(f"/tasks/{task_uuid}", headers=auth_headers)
        assert delete_response.status_code == 200

        # 6. Verify task no longer appears in results
        all_tasks_response = client.get("/tasks/", headers=auth_headers)
        all_tasks = all_tasks_response.json()
        remaining_task_uuids = [t["task_uuid"] for t in all_tasks]
        assert task_uuid not in remaining_task_uuids

    def test_task_assignment_workflow(self, client, auth_headers, test_user2):
        """Test task assignment and reassignment workflow."""
        # Create task
        task_data = {
            "title": "Assignment Test Task",
            "description": "Testing assignment workflow",
            "status": Status.TO_DO,
            "priority": 1
        }
        
        create_response = client.post("/tasks/", json=task_data, headers=auth_headers)
        task_uuid = create_response.json()["task_uuid"]

        # Assign to user2
        assignment_data = {"user_uuid": str(test_user2.user_uuid)}
        assign_response = client.post(
            f"/tasks/{task_uuid}/assign",
            json=assignment_data,
            headers=auth_headers
        )
        assert assign_response.status_code == 200
        assert assign_response.json()["assigned_to"] == str(test_user2.user_uuid)

        # Test "assigned to me" filter
        my_tasks_response = client.get("/tasks/?assigned_to_me=true", headers=auth_headers)
        assert my_tasks_response.status_code == 200
        my_tasks = my_tasks_response.json()
        # Task should not appear in current user's "assigned to me" filter
        task_uuids = [t["task_uuid"] for t in my_tasks]
        assert task_uuid not in task_uuids

        # Unassign task
        unassign_data = {"user_uuid": None}
        unassign_response = client.post(
            f"/tasks/{task_uuid}/assign",
            json=unassign_data,
            headers=auth_headers
        )
        assert unassign_response.status_code == 200
        assert unassign_response.json()["assigned_to"] is None

    def test_task_filtering_combinations(self, client, auth_headers):
        """Test various combinations of task filters."""
        # Create multiple tasks with different attributes
        tasks_data = [
            {
                "title": "High Priority Task",
                "status": Status.TO_DO,
                "priority": 1,
                "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "tags": ["urgent"]
            },
            {
                "title": "Medium Priority Task", 
                "status": Status.IN_PROGRESS,
                "priority": 2,
                "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "tags": ["normal"]
            },
            {
                "title": "Low Priority Task",
                "status": Status.DONE,
                "priority": 3,
                "due_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
                "tags": ["low"]
            }
        ]

        created_tasks = []
        for task_data in tasks_data:
            response = client.post("/tasks/", json=task_data, headers=auth_headers)
            assert response.status_code == 200
            created_tasks.append(response.json())

        # Test status filtering
        todo_response = client.get(f"/tasks/?status={Status.TO_DO}", headers=auth_headers)
        todo_tasks = todo_response.json()
        assert len([t for t in todo_tasks if t["status"] == Status.TO_DO]) >= 1

        # Test date range filtering
        tomorrow = (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d")
        recent_response = client.get(f"/tasks/?due_date_to={tomorrow}", headers=auth_headers)
        recent_tasks = recent_response.json()
        assert len(recent_tasks) >= 1

        # Test pagination
        page1_response = client.get("/tasks/?skip=0&limit=2", headers=auth_headers)
        page1_tasks = page1_response.json()
        assert len(page1_tasks) <= 2

    def test_concurrent_task_operations(self, client, auth_headers):
        """Test handling of concurrent operations on the same task."""
        # Create a task
        task_data = {
            "title": "Concurrent Test Task",
            "description": "Testing concurrent operations",
            "status": Status.TO_DO,
            "priority": 2
        }
        
        create_response = client.post("/tasks/", json=task_data, headers=auth_headers)
        task_uuid = create_response.json()["task_uuid"]

        # Simulate concurrent updates
        update_data_1 = {"title": "Updated by User 1"}
        update_data_2 = {"description": "Updated by User 2"}

        response1 = client.put(f"/tasks/{task_uuid}", json=update_data_1, headers=auth_headers)
        response2 = client.put(f"/tasks/{task_uuid}", json=update_data_2, headers=auth_headers)

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verify final state
        get_response = client.get(f"/tasks/{task_uuid}", headers=auth_headers)
        final_task = get_response.json()
        
        # Last update should win
        assert final_task["description"] == update_data_2["description"]

    def test_redis_rate_limiting_integration(self, client, auth_headers):
        """Test Redis-based rate limiting integration."""
        from services.redis_manager import redis_manager
        
        # Skip test if Redis is not available
        if not redis_manager.is_connected():
            pytest.skip("Redis not available for rate limiting test")
        
        # Make multiple requests to test rate limiting
        responses = []
        for i in range(5):
            response = client.get("/tasks/", headers=auth_headers)
            responses.append(response)
        
        # All requests should succeed (under normal rate limits)
        for response in responses:
            assert response.status_code in [200, 429]  # 429 if rate limited
            
        # Check rate limiting headers are present
        last_response = responses[-1]
        if last_response.status_code == 200:
            assert "X-RateLimit-Limit" in last_response.headers
            assert "X-RateLimit-Remaining" in last_response.headers
            assert "X-RateLimit-Reset" in last_response.headers