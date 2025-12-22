import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Games } from './pages/Games';
import { Achievements } from './pages/Achievements';
import { Competitions } from './pages/Competitions';
import { Rewards } from './pages/Rewards';
import { Social } from './pages/Social';
import { Leaderboards } from './pages/Leaderboards';
import { useAuth } from './contexts/AuthContext';

function App() {
    const { user, logout } = useAuth();

    return (
        <div className="flex bg-bg-page min-h-screen text-text-primary font-sans">
            <Sidebar />
            <div className="flex-1 flex flex-col min-h-screen overflow-hidden">
                {/* Header */}
                <header className="bg-bg-surface-2 p-4 shadow flex justify-between items-center z-10">
                    <h1 className="text-xl font-bold">Gamification Platform</h1>
                    <div className="text-sm">
                        {user ? (
                            <div className="flex items-center gap-4">
                                <span>Logged in as {user.username}</span>
                                <button onClick={logout} className="text-red-400 hover:text-red-300">Logout</button>
                            </div>
                        ) : 'Not logged in'}
                    </div>
                </header>

                {/* Main Content */}
                <main className="flex-1 p-6 overflow-y-auto">
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        <Route path="/games" element={<Games />} />
                        <Route path="/achievements" element={<Achievements />} />
                        <Route path="/competitions" element={<Competitions />} />
                        <Route path="/rewards" element={<Rewards />} />
                        <Route path="/social" element={<Social />} />
                        <Route path="/leaderboards" element={<Leaderboards />} />
                    </Routes>
                </main>
            </div>
        </div>
    );
}

export default App;
