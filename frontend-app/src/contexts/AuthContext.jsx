import React, { createContext, useContext, useState, useEffect } from 'react';
import api, { executeRequest, setAuthToken } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(false);

    const fetchPoints = async () => {
        try {
            const data = await executeRequest('rewards_my_points');
            setUser(prev => ({ ...prev, points: data.available_points }));
        } catch (error) {
            console.error("Failed to fetch points", error);
        }
    };

    useEffect(() => {
        const handleUnauthorized = () => {
            logout();
            alert("Your session has expired. Please log in again.");
        };
        window.addEventListener('auth-unauthorized', handleUnauthorized);
        return () => window.removeEventListener('auth-unauthorized', handleUnauthorized);
    }, []);

    useEffect(() => {
        if (token) {
            setAuthToken(token);
            const username = localStorage.getItem('username');
            // Only fetch if user state is not already set (e.g., page refresh)
            // or if we simply want to ensure sync without overwriting blindly
            if (username && !user) {
                setUser({ username });
                fetchPoints();
            }
        }
    }, [token, user]); // Add user to deps to re-eval if it changes, though !user check handles it

    const login = async (username, password) => {
        setLoading(true);
        try {
            const data = await executeRequest('login_user', { username, password });
            if (data.access_token) {
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('username', username);

                // Update state
                const newUser = { username };
                setUser(newUser); // Set user immediately
                setToken(data.access_token); // Trigger effect? user is now set, so effect should skip

                // Explicitly set auth token for immediate requests
                setAuthToken(data.access_token);

                // Fetch points immediately
                await fetchPoints();

                return true;
            }
            return false;
        } catch (error) {
            console.error("Login failed", error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const register = async (username, password) => {
        setLoading(true);
        try {
            await executeRequest('register_user', { username, password });
            return true;
        } catch (error) {
            console.error("Registration failed", error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        setToken(null);
        setUser(null);
        setAuthToken(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, loading, fetchPoints }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
