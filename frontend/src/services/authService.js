const API_BASE_URL = 'http://localhost:8000';

class AuthService {
    async register(userData) {
        try {
            // Validate data before sending
            if (!userData.username || userData.username.length < 3) {
                throw new Error('Username must be at least 3 characters long');
            }
            if (!userData.password || userData.password.length < 6) {
                throw new Error('Password must be at least 6 characters long');
            }
            if (!userData.email || !userData.email.includes('@')) {
                throw new Error('Please provide a valid email address');
            }
            if (!userData.name || userData.name.length < 2) {
                throw new Error('Name must be at least 2 characters long');
            }

            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: userData.username.trim(),
                    email: userData.email.trim().toLowerCase(),
                    name: userData.name.trim(),
                    password: userData.password
                }),
            });

            if (!response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const error = await response.json();
                    // Handle validation errors
                    if (error.detail && Array.isArray(error.detail)) {
                        const messages = error.detail.map(err => err.msg || err.message).join(', ');
                        throw new Error(messages);
                    }
                    throw new Error(error.detail || 'Registration failed');
                } else {
                    throw new Error(`Registration failed with status: ${response.status}`);
                }
            }

            const text = await response.text();
            return text ? JSON.parse(text) : {};
        } catch (error) {
            console.error('Registration error:', error);
            throw error;
        }
    }

    async login(credentials) {
        try {
            // Fix: Use actual credentials parameter, not hardcoded values
            const response = await fetch(`${API_BASE_URL}/auth/login-json`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: credentials.username,
                    password: credentials.password
                })
            });

            if (!response.ok) {
                // Safe JSON parsing with content check
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    try {
                        const error = await response.json();
                        throw new Error(error.detail || 'Login failed');
                    } catch (parseError) {
                        throw new Error(`Login failed with status: ${response.status}`);
                    }
                } else {
                    throw new Error(`Login failed with status: ${response.status}`);
                }
            }

            // Safe response parsing
            const text = await response.text();
            if (!text) {
                throw new Error('Empty response from server');
            }

            const data = JSON.parse(text);
            
            // Store authentication data
            if (data.access_token) {
                localStorage.setItem('accessToken', data.access_token);
            }
            if (data.user) {
                localStorage.setItem('user', JSON.stringify(data.user));
            }
            
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    async logout() {
        try {
            const token = localStorage.getItem('accessToken');
            
            // Call backend logout endpoint
            if (token) {
                try {
                    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'Content-Type': 'application/json',
                        },
                    });
                    
                    if (response.ok) {
                        const data = await response.text();
                        console.log('Logout successful:', data ? JSON.parse(data) : {});
                    }
                } catch (logoutError) {
                    console.warn('Backend logout failed:', logoutError);
                }
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Always clear local storage
            localStorage.removeItem('accessToken');
            localStorage.removeItem('user');
        }
    }

    async getCurrentUser() {
        try {
            const token = localStorage.getItem('accessToken');
            
            if (!token) {
                throw new Error('No access token found');
            }

            const response = await fetch(`${API_BASE_URL}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                if (response.status === 401) {
                    // Clear invalid tokens
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('user');
                    throw new Error('Authentication expired');
                }
                
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    try {
                        const error = await response.json();
                        throw new Error(error.detail || 'Failed to get user info');
                    } catch (parseError) {
                        throw new Error(`Failed to get user info with status: ${response.status}`);
                    }
                } else {
                    throw new Error(`Failed to get user info with status: ${response.status}`);
                }
            }

            // Safe response parsing
            const text = await response.text();
            if (!text) {
                throw new Error('Empty response from server');
            }

            return JSON.parse(text);
        } catch (error) {
            console.error('Get current user error:', error);
            throw error;
        }
    }

    async refreshToken() {
        try {
            const token = localStorage.getItem('accessToken');
            
            if (!token) {
                throw new Error('No access token found');
            }

            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                if (response.status === 401) {
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('user');
                    throw new Error('Authentication expired');
                }
                
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    try {
                        const error = await response.json();
                        throw new Error(error.detail || 'Token refresh failed');
                    } catch (parseError) {
                        throw new Error(`Token refresh failed with status: ${response.status}`);
                    }
                } else {
                    throw new Error(`Token refresh failed with status: ${response.status}`);
                }
            }

            const text = await response.text();
            if (!text) {
                throw new Error('Empty response from server');
            }

            const data = JSON.parse(text);
            if (data.access_token) {
                localStorage.setItem('accessToken', data.access_token);
            }
            
            return data;
        } catch (error) {
            console.error('Token refresh error:', error);
            throw error;
        }
    }

    getToken() {
        return localStorage.getItem('accessToken');
    }

    getUser() {
        try {
            const userStr = localStorage.getItem('user');
            return userStr ? JSON.parse(userStr) : null;
        } catch (error) {
            console.error('Error parsing stored user data:', error);
            localStorage.removeItem('user');
            return null;
        }
    }

    isAuthenticated() {
        return !!this.getToken();
    }

    // Helper method for safe response parsing
    async parseResponse(response) {
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            const text = await response.text();
            if (!text) {
                return {};
            }
            try {
                return JSON.parse(text);
            } catch (error) {
                console.error('JSON parse error:', error);
                throw new Error('Invalid JSON response');
            }
        } else {
            const text = await response.text();
            return { message: text || 'No content' };
        }
    }

    // Helper method for authenticated requests
    async makeAuthenticatedRequest(url, options = {}) {
        const token = this.getToken();
        
        if (!token) {
            throw new Error('No authentication token available');
        }

        const defaultHeaders = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        };

        const requestOptions = {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, requestOptions);

            if (response.status === 401) {
                // Try to refresh token
                try {
                    await this.refreshToken();
                    // Retry with new token
                    requestOptions.headers.Authorization = `Bearer ${this.getToken()}`;
                    return await fetch(url, requestOptions);
                } catch (refreshError) {
                    // Refresh failed, clear auth data
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('user');
                    throw new Error('Authentication expired');
                }
            }

            return response;
        } catch (error) {
            console.error('Authenticated request error:', error);
            throw error;
        }
    }
}

export default new AuthService();