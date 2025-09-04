import { useState, useEffect } from 'react';
import './App.css'
import Login from './components/Login';
import Register from './components/Register';
import Navigation from './components/Navigation';
import TaskList from './components/TaskList';
import authService from './services/authService';

function App() {
    const [user, setUser] = useState(null);
    const [showRegister, setShowRegister] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if user is already logged in
        const checkAuth = async () => {
            try {
                if (authService.isAuthenticated()) {
                    const userData = await authService.getCurrentUser();
                    setUser(userData);
                }
            } catch (err) {
                console.error('Auth check failed:', err);
            } finally {
                setLoading(false);
            }
        };

        checkAuth();
    }, []);

    const handleLoginSuccess = async () => {
        try {
            const userData = await authService.getCurrentUser();
            setUser(userData);
        } catch (err) {
            console.error('Failed to get user data after login:', err);
        }
    };

    const handleRegisterSuccess = () => {
        setShowRegister(false);
        // Optionally auto-login after registration
    };

    const handleLogout = () => {
        setUser(null);
    };

    if (loading) {
        return <div className="loading">Loading...</div>;
    }

    return (
        <div className="App">
            <Navigation user={user} onLogout={handleLogout} />
            
            {user ? (
                <div className="main-content">
                    <h2>Dashboard</h2>
                    <p>Welcome to your task management dashboard!</p>
                    <TaskList userId={user.id} />
                </div>
            ) : (
                <div className="auth-container">
                    {showRegister ? (
                        <div>
                            <Register onRegisterSuccess={handleRegisterSuccess} />
                            <p>
                                Already have an account?{' '}
                                <button 
                                    className="link-button"
                                    onClick={() => setShowRegister(false)}
                                >
                                    Login here
                                </button>
                            </p>
                        </div>
                    ) : (
                        <div>
                            <Login onLoginSuccess={handleLoginSuccess} />
                            <p>
                                Don't have an account?{' '}
                                <button 
                                    className="link-button"
                                    onClick={() => setShowRegister(true)}
                                >
                                    Register here
                                </button>
                            </p>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

export default App
