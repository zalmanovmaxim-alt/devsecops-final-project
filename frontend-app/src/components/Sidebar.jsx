import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const SidebarItem = ({ to, label, icon }) => (
    <NavLink
        to={to}
        className={({ isActive }) =>
            `w-full text-left py-2 px-4 rounded transition-colors block mb-2 ${isActive ? 'bg-blue-600 text-white' : 'bg-bg-surface-2 text-text-primary hover:bg-gray-700'
            }`
        }
    >
        <span className="mr-2">{icon}</span> {label}
    </NavLink>
);

export const Sidebar = () => {
    const { user } = useAuth();
    return (
        <aside className="w-64 bg-bg-surface shadow-lg min-h-screen p-4 flex flex-col">
            {user && (
                <div className="mb-6 p-3 bg-bg-surface-2 rounded-lg border border-gray-700">
                    <div className="font-bold text-lg text-blue-400">{user.username}</div>
                    <div className="text-sm text-text-secondary">
                        Points: <span className="text-yellow-400 font-mono">{user.points !== undefined ? user.points : '...'}</span>
                    </div>
                </div>
            )}
            <SidebarItem to="/" label="Home" icon="🏠" />
            <SidebarItem to="/login" label="Login" icon="🔑" />
            <SidebarItem to="/register" label="Register" icon="📝" />
            <hr className="border-gray-700 my-4" />
            <SidebarItem to="/games" label="Games" icon="🎮" />
            <SidebarItem to="/achievements" label="Achievements" icon="🏆" />
            <SidebarItem to="/competitions" label="Competitions" icon="📊" />
            <SidebarItem to="/rewards" label="Rewards" icon="🎁" />
            <SidebarItem to="/social" label="Social" icon="👥" />
            <SidebarItem to="/leaderboards" label="Leaderboards" icon="📈" />
        </aside>
    );
};
