const API_BASE_URL = 'http://localhost:8000';

class UserService {
    async getUsers(filters = {}) {
        const token = localStorage.getItem('accessToken');
        
        // Build query parameters
        const params = new URLSearchParams();
        if (filters.skip) params.append('skip', filters.skip);
        if (filters.limit) params.append('limit', filters.limit);

        const response = await fetch(`${API_BASE_URL}/users?${params}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Failed to fetch users');
        }

        return response.json();
    }

    async getUserById(userId) {
        const token = localStorage.getItem('accessToken');
        
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('Failed to fetch user');
        }

        return response.json();
    }
}

export default new UserService();