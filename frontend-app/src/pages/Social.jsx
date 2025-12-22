import React from 'react';
import { SectionPage } from './SectionPage';

export const Social = () => {
    return (
        <SectionPage
            title="Social"
            description="👥 Social: Build teams, send personal challenges to colleagues, and track social activities."
            color="teal"
            defaultPreset="social_activity_feed"
            buttons={[
                { label: 'Create Team', action: 'social_teams_create', type: 'primary' },
                { label: 'Activity Feed', action: 'social_activity_feed', type: 'primary' },
                { label: 'Send Challenge', action: 'social_challenges_send', type: 'primary' },
                { label: 'Rivalries', action: 'social_rivalries', type: 'primary' },
                { label: 'Celebrations', action: 'social_celebrations', type: 'primary' },
            ]}
        />
    );
};
