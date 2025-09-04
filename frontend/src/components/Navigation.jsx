import React from 'react';
import authService from '../services/authService';

const Navigation = ({ user, onLogout }) => {
    const handleLogout = async () => {
        try {
            await authService.logout();
            onLogout && onLogout();
        } catch (err) {
            console.error('Logout error:', err);
        }
    };

    return (
        <nav className="navigation">
            <div className="nav-brand">
                <h1>Task-O-Matic</h1>
            </div>
            <div className="nav-items">
                {user ? (
                    <>
                        <span>Welcome, {user.name}!</span>
                        <button onClick={handleLogout}>Logout</button>
                    </>
                ) : (
                    <span>Please log in</span>
                )}
            </div>
        </nav>
    );
};

export default Navigation;