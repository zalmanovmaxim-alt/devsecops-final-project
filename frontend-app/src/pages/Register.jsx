import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { CardHeader } from '../components/Card';

export const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { register } = useAuth();

    const handleRegister = async () => {
        try {
            await register(username, password);
            alert('Account created successfully! Please login.');
        } catch (e) {
            alert('Registration error: ' + e.message);
        }
    };

    return (
        <div className="max-w-md mx-auto">
            <h2 className="text-2xl mb-4">Register</h2>
            <CardHeader
                title="📝 Register: Create a new account to join the gamification platform. Choose a unique username and secure password."
                color="purple"
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
                    onClick={handleRegister}
                    className="bg-matte-blue hover:bg-matte-blue-hover text-white px-4 py-2 rounded w-full"
                >
                    Register
                </button>
            </div>
        </div>
    );
};
