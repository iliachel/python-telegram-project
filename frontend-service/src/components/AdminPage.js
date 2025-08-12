import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import TelegramAdmin from './TelegramAdmin'; // Import the new component

const AdminPage = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        try {
            await logout();
            navigate('/login');
        } catch (error) {
            console.error("Failed to logout", error);
        }
    };

    return (
        <div>
            <h2>Admin Panel</h2>
            <p>Welcome, {user ? user.username : 'Guest'}!</p>
            <button onClick={handleLogout}>Logout</button>
            <hr />
            <TelegramAdmin /> {/* Render the new component */}
        </div>
    );
};

export default AdminPage;
