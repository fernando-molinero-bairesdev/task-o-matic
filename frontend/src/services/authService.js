const API_BASE_URL = 'http://localhost:8000';

class AuthService {
    async register(userData) {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        return response.json();
    }

    async login(credentials) {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        localStorage.setItem('accessToken', data.access_token);
        return data;
    }

    async logout() {
        const token = localStorage.getItem('accessToken');
        
        if (token) {
            await fetch(`${API_BASE_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });
        }

        localStorage.removeItem('accessToken');
    }

    async getCurrentUser() {
        const token = localStorage.getItem('accessToken');
        
        if (!token) {
            throw new Error('No access token found');
        }

        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            localStorage.removeItem('accessToken'); // Remove invalid token
            throw new Error('Failed to get user info');
        }

        return response.json();
    }

    getToken() {
        return localStorage.getItem('accessToken');
    }

    isAuthenticated() {
        return !!this.getToken();
    }
}

export default new AuthService();