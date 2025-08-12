import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if the user is already logged in (e.g., by checking the cookie)
        const checkLoggedIn = async () => {
            try {
                // Set withCredentials to true to send cookies with the request
                const response = await axios.get(`${API_URL}/user`, { withCredentials: true });
                if (response.data.username) {
                    setUser({ username: response.data.username });
                }
            } catch (error) {
                setUser(null);
            } finally {
                setLoading(false);
            }
        };
        checkLoggedIn();
    }, []);

    const login = async (username, password) => {
        const response = await axios.post(`${API_URL}/login`, { username, password }, { withCredentials: true });
        if (response.data.status === 'success') {
            setUser({ username: response.data.username });
        }
        return response;
    };

    const register = async (username, email, password) => {
        return await axios.post(`${API_URL}/register`, { username, email, password });
    };

    const logout = async () => {
        await axios.post(`${API_URL}/logout`, {}, { withCredentials: true });
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, setUser, login, register, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    return useContext(AuthContext);
};
