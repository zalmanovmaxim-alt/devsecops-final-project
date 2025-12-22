import React from 'react';
import { SectionPage } from './SectionPage';
// Note: Competitions page in original had a specific Join Modal with tiles. 
// For this port, we will use the standard list buttons for simplicity, or we can add a specific "Join" button that maps to `competitions_join`.

export const Competitions = () => {
    return (
        <SectionPage
            title="Competitions"
            description="📊 Competitions: Join predefined office competition categories like Code Quality, Learning, Fitness, Sustainability."
            color="indigo"
            defaultPreset="competitions_my_competitions"
            buttons={[
                { label: 'My Competitions', action: 'competitions_my_competitions', type: 'primary' },
                { label: 'All Competitions', action: 'competitions_all', type: 'primary' },
                { label: 'Join (ID)', action: 'competitions_join', type: 'secondary' },
                // We could add buttons for specific join types if we wanted to be exhaustive
            ]}
        />
    );
};
