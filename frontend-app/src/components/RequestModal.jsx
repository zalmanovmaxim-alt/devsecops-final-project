import React, { useState, useEffect } from 'react';
import { PRESETS } from '../services/api';

export const RequestModal = ({ presetName, isOpen, onClose, onSubmit }) => {
    const [formData, setFormData] = useState({});
    const preset = PRESETS[presetName];

    useEffect(() => {
        if (preset && preset.template) {
            // Initialize form with template values, or dynamic defaults
            const defaults = { ...preset.template };
            // Handle special cases (start_at, end_at logic from app.js)
            if (presetName === 'games_create') {
                const now = new Date();
                defaults.start_at = now.toLocaleDateString('en-GB');
                defaults.end_at = new Date(now.getTime() + 7 * 86400000).toLocaleDateString('en-GB');
            }
            setFormData(defaults);
        }
    }, [presetName, preset]);

    if (!isOpen || !preset) return null;

    const handleSubmit = () => {
        onSubmit(formData);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-bg-surface p-6 rounded-lg w-full max-w-lg shadow-xl border border-gray-700">
                <h3 className="text-xl font-bold mb-4 text-text-primary">
                    {presetName.replace(/_/g, ' ')}
                </h3>

                <div className="space-y-3 mb-6">
                    {Object.entries(formData).map(([key, value]) => {
                        if (key === 'is_active') return null; // Skip hidden fields

                        return (
                            <div key={key} className="flex flex-col gap-1">
                                <label className="text-sm font-semibold capitalize text-text-secondary">{key.replace(/_/g, ' ')}</label>
                                {key === 'rarity' ? (
                                    <select
                                        className="bg-bg-surface-2 border border-gray-600 rounded p-2 text-text-primary"
                                        value={value}
                                        onChange={e => setFormData({ ...formData, [key]: e.target.value })}
                                    >
                                        <option value="common">Common (10)</option>
                                        <option value="rare">Rare (20)</option>
                                        <option value="epic">Epic (40)</option>
                                        <option value="legendary">Legendary (80)</option>
                                    </select>
                                ) : (
                                    <input
                                        className="bg-bg-surface-2 border border-gray-600 rounded p-2 text-text-primary w-full"
                                        value={value}
                                        onChange={e => setFormData({ ...formData, [key]: e.target.value })}
                                    />
                                )}
                            </div>
                        );
                    })}
                </div>

                <div className="flex justify-end gap-2">
                    <button onClick={onClose} className="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded text-white">Cancel</button>
                    <button onClick={handleSubmit} className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded text-white">Submit</button>
                </div>
            </div>
        </div>
    );
};
