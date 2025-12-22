import React from 'react';
import { SectionPage } from './SectionPage';

export const Leaderboards = () => {
    return (
        <SectionPage
            title="Leaderboards"
            description="📈 Leaderboards: View rankings across different categories - Global, Team, Monthly, and Hall of Fame."
            color="red"
            defaultPreset="leaderboards_global"
            buttons={[
                { label: 'Global', action: 'leaderboards_global', type: 'primary' },
                { label: 'Team', action: 'leaderboards_team', type: 'primary' },
                { label: 'Monthly', action: 'leaderboards_monthly', type: 'primary' },
                { label: 'Hall of Fame', action: 'leaderboards_hall_of_fame', type: 'primary' },
                { label: 'Add Entry', action: 'leaderboards_add', type: 'secondary' },
            ]}
        />
    );
};
