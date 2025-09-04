const API_BASE_URL = 'http://localhost:8000';

class TaskService {
    async getTasks(filters = {}) {
        const token = localStorage.getItem('accessToken');
        
        // Build query parameters
        const params = new URLSearchParams();
        if (filters.skip) params.append('skip', filters.skip);
        if (filters.limit) params.append('limit', filters.limit);
        if (filters.status) params.append('status', filters.status);
        if (filters.due_date_from) params.append('due_date_from', filters.due_date_from);
        if (filters.due_date_to) params.append('due_date_to', filters.due_date_to);
        if (filters.assigned_to_me) params.append('assigned_to_me', filters.assigned_to_me);

        const response = await fetch(`${API_BASE_URL}/tasks?${params}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Failed to fetch tasks');
        }

        return response.json();
    }

    async getTaskStatuses() {
        const response = await fetch(`${API_BASE_URL}/tasks/statuses`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch task statuses');
        }

        return response.json();
    }

    async createTask(taskData) {
        const token = localStorage.getItem('accessToken');
        
        const response = await fetch(`${API_BASE_URL}/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(taskData),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create task');
        }

        return response.json();
    }

    async updateTask(taskId, taskData) {
        const token = localStorage.getItem('accessToken');
        
        // Add validation for taskId
        if (!taskId) {
            throw new Error('Task ID is required for updating');
        }
        
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(taskData),
        });

        if (!response.ok) {
            throw new Error('Failed to update task');
        }

        return response.json();
    }

    async deleteTask(taskId) {
        const token = localStorage.getItem('accessToken');
        
        // Add validation for taskId
        if (!taskId) {
            throw new Error('Task ID is required for deletion');
        }
        
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Failed to delete task');
        }

        return response.json();
    }

    async assignTask(taskId, userId) {
        const token = localStorage.getItem('accessToken');
        
        // Add validation for taskId
        if (!taskId) {
            throw new Error('Task ID is required for assignment');
        }
        
        console.log('Assigning task:', taskId, 'to user:', userId);
        
        // Prepare the request body - userId can be null for unassignment
        const requestBody = {
            user_uuid: userId
        };
        
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/assign`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Assign task error response:', errorText);
            
            // Try to parse as JSON for better error messages
            try {
                const errorJson = JSON.parse(errorText);
                throw new Error(errorJson.detail || `Failed to assign task: ${response.status}`);
            } catch (parseError) {
                throw new Error(`Failed to assign task: ${response.status} - ${errorText}`);
            }
        }

        return response.json();
    }

    async completeTask(taskId) {
        const token = localStorage.getItem('accessToken');
        
        // Add validation for taskId
        if (!taskId) {
            throw new Error('Task ID is required for completion');
        }
        
        console.log('Completing task with ID:', taskId);
        
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/complete`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Complete task error:', errorText);
            throw new Error(`Failed to complete task: ${errorText}`);
        }

        return response.json();
    }
}

export default new TaskService();