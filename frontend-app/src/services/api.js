import axios from 'axios';

// Requests will be prefixed with /api to be intercepted by Nginx
const API_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const setAuthToken = (token) => {
    if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
        delete api.defaults.headers.common['Authorization'];
    }
};

// Mapped from presets.txt with body templates
export const PRESETS = {
    register_user: { url: "/register", method: "POST", template: { username: "", password: "" } },
    login_user: { url: "/login", method: "POST", template: { username: "", password: "" } },

    achievements_available: { url: "/achievements/available", method: "GET" },
    achievements_unlock: { url: "/achievements/unlock", method: "POST", template: { achievement_id: 1 } },
    achievements_my_progress: { url: "/achievements/my-progress", method: "GET" },
    achievements_create_custom: { url: "/achievements/create-custom", method: "POST", template: { name: "", description: "", rarity: "common" } },
    achievements_achievement_remove: { url: "/achievements/achievement/remove", method: "DELETE", template: { id: "" } },
    achievements_user_achievement_remove: { url: "/achievements/user-achievement/remove", method: "DELETE", template: { id: "" } },

    games_create: { url: "/games/create", method: "POST", template: { title: "", description: "", start_at: "", end_at: "", is_active: true } },
    games_active: { url: "/games/active", method: "GET" },
    games_join: { url: "/games/join", method: "POST", template: { competition_id: 1 } },
    games_progress_update: { url: "/games/progress/update", method: "PUT", template: { competition_id: "", delta: "" } },
    games_rules_update: { url: "/games/rules/update", method: "GET" },
    games_competition_remove: { url: "/games/competition/remove", method: "DELETE", template: { id: "" } },
    games_participation_remove: { url: "/games/participation/remove", method: "DELETE", template: { id: "" } },
    games_leave: { url: "/games/leave", method: "DELETE", template: { competition_id: "" } },
    games_game_remove: { url: "/games/game/remove", method: "DELETE", template: { id: "" } },

    competitions_my_competitions: { url: "/competitions/my-competitions", method: "GET" },
    competitions_all: { url: "/competitions/all", method: "GET" },
    competitions_join: { url: "/competitions/join", method: "POST", template: { competition_id: "" } },
    competitions_leave: { url: "/competitions/leave", method: "DELETE", template: { competition_id: "" } },
    competitions_remove: { url: "/competitions/remove", method: "DELETE", template: { competition_id: "" } },
    competitions_joined: { url: "/competitions/joined", method: "GET" },

    // Competition types (POST)
    competitions_code_quality: { url: "/competitions/code-quality", method: "POST" },
    competitions_learning: { url: "/competitions/learning", method: "POST" },
    competitions_fitness: { url: "/competitions/fitness", method: "POST" },
    competitions_sustainability: { url: "/competitions/sustainability", method: "POST" },
    competitions_creativity: { url: "/competitions/creativity", method: "POST" },
    competitions_team_building: { url: "/competitions/team-building", method: "POST" },

    leaderboards_global: { url: "/leaderboards/global", method: "GET" },
    leaderboards_team: { url: "/leaderboards/team", method: "GET" },
    leaderboards_monthly: { url: "/leaderboards/monthly", method: "GET" },
    leaderboards_hall_of_fame: { url: "/leaderboards/hall-of-fame", method: "GET" },
    leaderboards_predictions: { url: "/leaderboards/predictions", method: "POST", template: { prediction: "" } },
    leaderboards_predictions_view: { url: "/leaderboards/predictions", method: "GET" },
    leaderboards_predictions_remove: { url: "/leaderboards/predictions/remove", method: "DELETE", template: { id: 1 } },
    leaderboards_add: { url: "/leaderboards/add", method: "POST", template: { user: "", points: "", board: "global" } },
    leaderboards_remove: { url: "/leaderboards/remove", method: "DELETE", template: { id: "" } },

    rewards_available: { url: "/rewards/available", method: "GET" },
    rewards_my_points: { url: "/rewards/my-points", method: "GET" },
    rewards_donate_points: { url: "/rewards/donate-points", method: "POST", template: { recipient: "", amount: "" } },
    rewards_redeem: { url: "/rewards/redeem", method: "POST", template: { reward_id: "" } },
    rewards_add: { url: "/rewards/add", method: "POST", template: { name: "", points: "" } },
    rewards_remove: { url: "/rewards/remove", method: "DELETE", template: { id: "" } },

    social_teams_create: { url: "/social/teams/create", method: "POST", template: { team_name: "", members: [] } },
    social_friends: { url: "/social/friends", method: "GET" },
    social_challenges_send: { url: "/social/challenges/send", method: "POST", template: { to: "", challenge: "" } },
    social_challenges_view: { url: "/social/challenges/view", method: "GET" },
    social_activity_feed: { url: "/social/activity-feed", method: "GET" },
    social_celebrations: { url: "/social/celebrations", method: "GET" },
    social_rivalries: { url: "/social/rivalries", method: "GET" },
    social_activity_remove: { url: "/social/activity/remove", method: "DELETE", template: { id: "" } },
    social_challenges_remove: { url: "/social/challenges/remove", method: "DELETE", template: { id: "" } },

    // Special endpoint
    players_grouped: { url: "/players_grouped", method: "GET" }
};

export const executeRequest = async (presetName, data = {}) => {
    const preset = PRESETS[presetName];
    if (!preset) throw new Error(`Unknown preset: ${presetName}`);

    const config = {
        method: preset.method,
        url: preset.url,
    };

    if (preset.method === 'GET') {
        config.params = data;
    } else {
        config.data = data;
    }

    const response = await api(config);
    return response.data;
};

// Add interceptor to notify on 401
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Option 1: Broadcast event
            window.dispatchEvent(new Event('auth-unauthorized'));
        }
        return Promise.reject(error);
    }
);

export default api;
