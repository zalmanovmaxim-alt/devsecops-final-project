import React from 'react';

// Helper to prettify keys (snake_case -> Title Case with spaces)
const prettify = (str) => {
    return str.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
};

const TableAction = ({ label, onClick, className }) => (
    <button
        onClick={onClick}
        className={`px-2 py-1 rounded text-xs text-white block mx-auto w-full mb-1 ${className}`}
    >
        {label}
    </button>
);

export const DynamicTable = ({ data, onAction }) => {
    if (!data) return <p className="text-gray-400">No data available</p>;
    if (typeof data === 'string') return <p className="text-gray-300">{data}</p>;

    // 1. Determine the array to render
    let dataArray = null;
    if (Array.isArray(data)) {
        dataArray = data;
    } else if (typeof data === 'object') {
        const preferred = ['rewards', 'leaderboard', 'predictions', 'hall_of_fame', 'items', 'data', 'store', 'unlocked', 'locked'];
        for (const k of preferred) {
            if (Array.isArray(data[k])) { dataArray = data[k]; break; }
        }
        if (!dataArray) {
            const arrayKeys = Object.keys(data).filter(k => Array.isArray(data[k]));
            if (arrayKeys.length === 1) dataArray = data[arrayKeys[0]];
        }
    }

    // 2. Fallback for Key-Value display if no array found
    if (!Array.isArray(dataArray)) {
        return (
            <table className="table-auto border-collapse border border-gray-700 w-full text-sm">
                <thead className="bg-bg-surface-2">
                    <tr>
                        <th className="border border-gray-700 px-2 py-1 text-center">Field</th>
                        <th className="border border-gray-700 px-2 py-1 text-center">Value</th>
                    </tr>
                </thead>
                <tbody>
                    {Object.entries(data).map(([k, v]) => (
                        <tr key={k}>
                            <td className="border border-gray-700 px-2 py-1 text-left bg-bg-surface-2 font-semibold text-text-secondary">{prettify(k)}</td>
                            <td className="border border-gray-700 px-2 py-1 text-center text-text-primary">
                                {(typeof v === 'object' && v !== null) ? JSON.stringify(v) : String(v)}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        );
    }

    if (dataArray.length === 0) return <p className="text-gray-400">Empty list</p>;

    // 3. Render Array Data
    // Determine headers
    let allHeaders = [...new Set(dataArray.flatMap(obj => obj && typeof obj === 'object' ? Object.keys(obj) : []))];
    const hasId = allHeaders.includes('id');

    // Logic from original app.js to determine table type
    const isLeaderboard = allHeaders.includes('achievements') && allHeaders.includes('points');
    const isTeamLeaderboard = isLeaderboard && allHeaders.includes('team_name');
    const isAchievements = allHeaders.includes('name') && allHeaders.includes('description') && allHeaders.includes('locked');
    const isGames = allHeaders.includes('title') && allHeaders.includes('description') && allHeaders.includes('start_at');
    const isRewards = allHeaders.includes('name') && allHeaders.includes('points') && hasId;

    // Define columns to show
    let headers = allHeaders;
    if (isTeamLeaderboard) headers = ['user', 'team_name', 'achievements', 'points'];
    else if (isLeaderboard) headers = ['user', 'achievements', 'points'];
    else if (isAchievements) headers = ['name', 'description', 'rarity', 'user_unlocked'];
    else if (isGames) {
        headers = ['title', 'description', 'participants', 'duration']; // We need to compute duration
    }
    // Filter to ensure headers exist in data
    headers = headers.filter(h => allHeaders.includes(h) || h === 'duration' || h === 'participants');

    // Remove 'id' from display cols if generic
    if (!isLeaderboard && !isAchievements && !isGames && hasId) {
        headers = headers.filter(h => h !== 'id');
    }

    const needsActions = hasId || isGames || isRewards;

    return (
        <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-700 text-sm">
                <thead className="bg-bg-surface-2">
                    <tr>
                        {headers.map(h => <th key={h} className="border border-gray-700 px-3 py-2 text-center text-text-secondary">{prettify(h)}</th>)}
                        {needsActions && <th className="border border-gray-700 px-3 py-2 text-center text-text-secondary">Actions</th>}
                    </tr>
                </thead>
                <tbody>
                    {dataArray.map((row, idx) => {
                        // Pre-process row for special fields
                        if (isGames) {
                            if (row.start_at && row.end_at) {
                                const start = new Date(row.start_at).toLocaleDateString('en-GB');
                                const end = new Date(row.end_at).toLocaleDateString('en-GB');
                                // Add virtual property for rendering
                                row.duration = `${start} - ${end}`;
                            }
                        }

                        return (
                            <tr key={row.id || idx} className="hover:bg-bg-surface-2 transition-colors">
                                {headers.map(h => {
                                    let val = row[h];
                                    if (h === 'achievements' && Array.isArray(val)) {
                                        val = val.map(a => <div key={a.name} className="text-xs">{a.name}</div>);
                                    } else if (h === 'participants' && Array.isArray(val)) {
                                        val = val.map((p, i) => <div key={i} className="text-xs">{p.username || p.user || p}</div>);
                                    } else if (typeof val === 'object' && val !== null) {
                                        val = JSON.stringify(val);
                                    }
                                    return <td key={h} className="border border-gray-700 px-3 py-2 text-center">{val}</td>
                                })}

                                {needsActions && (
                                    <td className="border border-gray-700 px-3 py-2 text-center">
                                        {isAchievements && (
                                            <>
                                                <TableAction label="Unlock" className="bg-green-600 hover:bg-green-700" onClick={() => onAction('unlock', row)} />
                                                <TableAction label="Lock" className="bg-yellow-600 hover:bg-yellow-700" onClick={() => onAction('lock', row)} />
                                                <TableAction label="Remove" className="bg-red-600 hover:bg-red-700" onClick={() => onAction('remove', row)} />
                                            </>
                                        )}
                                        {((isGames && !isAchievements) || (isRewards)) && (
                                            <>
                                                {isGames && <TableAction label="Join" className="bg-green-600 hover:bg-green-700" onClick={() => onAction('join', row)} />}
                                                {isRewards && <TableAction label="Redeem" className="bg-green-600 hover:bg-green-700" onClick={() => onAction('redeem', row)} />}
                                                <TableAction label="Remove" className="bg-red-600 hover:bg-red-700" onClick={() => onAction('remove', row)} />
                                            </>
                                        )}
                                        {/* Fallback remove */}
                                        {!isAchievements && !isGames && !isRewards && (
                                            <TableAction label="Remove" className="bg-red-600 hover:bg-red-700" onClick={() => onAction('remove', row)} />
                                        )}
                                    </td>
                                )}
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
};
