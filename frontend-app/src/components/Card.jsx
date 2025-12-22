import React from 'react';

export const Card = ({ children, className = '' }) => (
    <div className={`bg-bg-surface text-text-primary rounded-lg shadow p-4 ${className}`}>
        {children}
    </div>
);

export const CardHeader = ({ title, color = 'blue' }) => {
    const borderColors = {
        blue: 'border-blue-400',
        green: 'border-green-400',
        purple: 'border-purple-400',
        orange: 'border-orange-400',
        yellow: 'border-yellow-400',
        red: 'border-red-400',
        pink: 'border-pink-400',
        teal: 'border-teal-400',
        indigo: 'border-indigo-400'
    };

    const textColors = {
        blue: 'text-blue-200',
        green: 'text-green-200',
        purple: 'text-purple-200',
        orange: 'text-orange-200',
        yellow: 'text-yellow-200',
        red: 'text-red-200',
        pink: 'text-pink-200',
        teal: 'text-teal-200',
        indigo: 'text-indigo-200'
    };

    return (
        <div className={`bg-gray-800 border-l-4 ${borderColors[color] || 'border-blue-400'} p-4 mb-6 rounded-r`}>
            <p className={`${textColors[color] || 'text-blue-200'}`}>
                <strong>{title}</strong>
            </p>
        </div>
    );
};
