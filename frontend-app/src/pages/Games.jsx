import React from 'react';
import { SectionPage } from './SectionPage';

export const Games = () => {
    return (
        <SectionPage
            title="Games"
            description="🎮 Games: Create and manage custom game competitions. Set up tournaments, track participant progress, and define custom game rules."
            color="orange"
            defaultPreset="games_active"
            buttons={[
                { label: 'Create', action: 'games_create', type: 'primary' },
                { label: 'Active', action: 'games_active', type: 'primary' },
                { label: 'Update Progress', action: 'games_progress_update', type: 'primary' },
            ]}
        />
    );
};
