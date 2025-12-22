import React from 'react';
import { SectionPage } from './SectionPage';

export const Rewards = () => {
    return (
        <SectionPage
            title="Rewards"
            description="🎁 Rewards: Redeem your earned points for rewards and manage the reward catalog."
            color="pink"
            defaultPreset="rewards_available"
            buttons={[
                { label: 'Available', action: 'rewards_available', type: 'primary' },
                { label: 'Add Reward', action: 'rewards_add', type: 'primary' },
                { label: 'Donate Points', action: 'rewards_donate_points', type: 'primary' },
            ]}
        />
    );
};
