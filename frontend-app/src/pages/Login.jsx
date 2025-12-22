import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { CardHeader } from '../components/Card';

export const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleLogin = async () => {
        try {
            const success = await login(username, password);
            if (success) {
                alert('Login successful!');
                navigate('/');
            } else {
                alert('Login failed');
            }
        } catch (e) {
            alert('Login error: ' + e.message);
        }
    };

    return (
        <div className="max-w-md mx-auto">
            <h2 className="text-2xl mb-4">Login</h2>
            <CardHeader
                title="🔑 Login: Sign in to your account to access personalized features, track your progress, and participate in competitions."
                color="green"
            />

            <div className="space-y-4">
                <input
                    className="w-full bg-bg-surface-2 border border-gray-700 p-2 rounded text-text-primary"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    type="password"
                    className="w-full bg-bg-surface-2 border border-gray-700 p-2 rounded text-text-primary"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button
                    onClick={handleLogin}
                    className="bg-matte-blue hover:bg-matte-blue-hover text-white px-4 py-2 rounded w-full"
                >
                    Login
                </button>
            </div>
        </div>
    );
};
