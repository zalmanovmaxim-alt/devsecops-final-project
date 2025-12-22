import React, { useEffect, useState } from 'react';
import { Card, CardHeader } from '../components/Card';
import { executeRequest } from '../services/api';
import { DynamicTable } from '../components/DynamicTable';

export const Home = () => {
    const [players, setPlayers] = useState([]);

    useEffect(() => {
        const fetchPlayers = async () => {
            try {
                const data = await executeRequest('players_grouped');
                setPlayers(data);
            } catch (err) {
                console.error(err);
            }
        };
        fetchPlayers();
        const interval = setInterval(fetchPlayers, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold">Welcome to the Gamification Platform</h2>

            <CardHeader
                title="🏠 Home Dashboard: View the main overview of all players, their competitions, and total points. This is your central hub for monitoring office gamification progress."
                color="blue"
            />

            <p className="text-text-secondary">
                Use the sidebar to navigate through different sections. Start by logging in or registering a new account.
            </p>

            <h3 className="text-xl font-semibold">🎮 Players</h3>
            <Card>
                <DynamicTable data={players} />
            </Card>
        </div>
    );
};
