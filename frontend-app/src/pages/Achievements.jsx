import React from 'react';
import { SectionPage } from './SectionPage';

export const Achievements = () => {
    return (
        <SectionPage
            title="Achievements"
            description="🏆 Achievements: Unlock and manage achievement badges with rarity-based point values."
            color="yellow"
            defaultPreset="achievements_available"
            buttons={[
                { label: 'Available', action: 'achievements_available', type: 'primary' },
                { label: 'Custom', action: 'achievements_create_custom', type: 'primary' },
                { label: 'My Progress', action: 'achievements_my_progress', type: 'secondary' },
            ]}
        />
    );
};
