import React, { useState, useEffect } from 'react';
import { Card, CardHeader } from '../components/Card';
import { executeRequest, PRESETS } from '../services/api';
import { DynamicTable } from '../components/DynamicTable';
import { RequestModal } from '../components/RequestModal';
import { useAuth } from '../contexts/AuthContext';

export const SectionPage = ({ title, description, color, buttons, defaultPreset }) => {
    const [data, setData] = useState(null);
    const [currentPreset, setCurrentPreset] = useState(defaultPreset);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalPreset, setModalPreset] = useState(null);
    const { fetchPoints } = useAuth();

    const fetchData = async (presetName = currentPreset) => {
        try {
            const result = await executeRequest(presetName);
            setData(result);
            setCurrentPreset(presetName);
        } catch (err) {
            console.error(err);
            alert("Request failed: " + err.message);
        }
    };

    useEffect(() => {
        if (defaultPreset) fetchData(defaultPreset);
    }, [defaultPreset]);

    const handleButtonClick = async (btn) => {
        const preset = PRESETS[btn.action];

        // If it requires input (has template) and is not GET, open modal
        if (preset.template && Object.keys(preset.template).length > 0) {
            setModalPreset(btn.action);
            setIsModalOpen(true);
        } else {
            // Direct execution (GET or simple POST)
            await fetchData(btn.action);
        }
    };

    const handleModalSubmit = async (formData) => {
        try {
            await executeRequest(modalPreset, formData);
            // Refresh current view if possible
            fetchData(currentPreset);
            // Refresh points in case it was a donation or reward or game join
            await fetchPoints();
        } catch (e) {
            alert('Error: ' + e.message);
        }
    };

    const handleTableAction = async (actionType, row) => {
        let presetName = null;
        let body = {};

        if (actionType === 'join') {
            if (currentPreset.includes('competitions')) {
                presetName = 'competitions_join';
                body = { competition_id: row.id };
            } else if (currentPreset.includes('games')) {
                presetName = 'games_join';
                body = { competition_id: row.id };
            }
        } else if (actionType === 'redeem') {
            presetName = 'rewards_redeem';
            body = { reward_id: row.id };
        } else if (actionType === 'remove') {
            if (currentPreset.includes('rewards')) {
                presetName = 'rewards_remove';
                body = { id: row.id };
            } else if (currentPreset.includes('competitions')) {
                presetName = 'competitions_remove';
                body = { competition_id: row.id };
            } else if (currentPreset.includes('games')) {
                if (currentPreset.includes('active')) {
                    presetName = 'games_leave';
                    body = { competition_id: row.id };
                } else {
                    presetName = 'games_game_remove';
                    body = { id: row.id };
                }
            } else if (currentPreset.includes('leaderboards')) {
                if (currentPreset.includes('predictions')) {
                    presetName = 'leaderboards_predictions_remove';
                    body = { id: row.id };
                } else {
                    presetName = 'leaderboards_remove';
                    body = { id: row.id };
                }
            } else if (currentPreset.includes('social')) {
                if (currentPreset.includes('challenges')) {
                    presetName = 'social_challenges_remove';
                    body = { id: row.id };
                } else {
                    presetName = 'social_activity_remove';
                    body = { id: row.id };
                }
            } else if (currentPreset.includes('achievements')) {
                // Determine if we are removing the achievement definition or the user unlock?
                // DynamicTable probably shows 'Remove' if not unlockable?
                // Actually DynamicTable logic:
                // if isAchievements: Unlock, Lock, Remove.
                // Remove -> ???
                // If the user clicks 'Remove' on an achievement list, it's likely removing the definition (admin)
                // BUT if it's "My Progress", maybe removing the unlock?
                // Let's assume removing definition for 'available' and unlock for 'my progress' if applicable?
                // Actually simpler: 
                if (currentPreset.includes('my-progress')) {
                    // Removing from "My Progress" is ambiguous. Does the user want to relinquish the achievement?
                    // Or delete the global definition?
                    // To prevent data loss (negative points), we will BLOCK this action or map it to a safe "Hide" if implemented.
                    // For now, let's treat it as "Delete Definition" (Soft Delete) IF the user has permission?
                    // But standard users shouldn't delete definitions.
                    // SAFEST: Block it.
                    console.log("Remove action blocked in My Progress to prevent point loss.");
                    alert("Cannot remove unlocked achievements from progress history.");
                    return;
                } else {
                    presetName = 'achievements_achievement_remove';
                    body = { id: row.id };
                }
            }
        } else if (actionType === 'unlock') {
            presetName = 'achievements_unlock';
            body = { achievement_id: row.id };
        }

        if (presetName) {
            try {
                await executeRequest(presetName, body);
                alert(`${actionType} successful!`);
                fetchData(currentPreset);
                // Refresh points
                await fetchPoints();
            } catch (e) {
                console.error(e);
                alert(`Error: ${e.message}`);
            }
        } else {
            console.log("Table action not implemented", actionType, row);
            alert(`${actionType} action not configured for this section.`);
        }
    };

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold">{title}</h2>
            <CardHeader title={description} color={color} />

            <div className="flex gap-2 flex-wrap">
                {buttons.map((btn, idx) => (
                    <button
                        key={idx}
                        onClick={() => handleButtonClick(btn)}
                        className={`px-4 py-2 rounded text-white ${btn.type === 'primary' ? 'bg-blue-600 hover:bg-blue-500' : 'bg-gray-600 hover:bg-gray-500'
                            }`}
                    >
                        {btn.label}
                    </button>
                ))}
            </div>

            <Card>
                <DynamicTable data={data} onAction={handleTableAction} />
            </Card>

            <RequestModal
                isOpen={isModalOpen}
                presetName={modalPreset}
                onClose={() => setIsModalOpen(false)}
                onSubmit={handleModalSubmit}
            />
        </div>
    );
};
