import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';

// Mock API to avoid network calls
vi.mock('../services/api', () => ({
    executeRequest: vi.fn(),
    setAuthToken: vi.fn(),
    PRESETS: {}
}));

describe('App', () => {
    it('renders Sidebar and Header', () => {
        render(
            <BrowserRouter>
                <AuthProvider>
                    <App />
                </AuthProvider>
            </BrowserRouter>
        );

        expect(screen.getByText(/Gamification Platform/i)).toBeInTheDocument();
        expect(screen.getByText(/Home/i)).toBeInTheDocument();
        expect(screen.getByText(/Login/i)).toBeInTheDocument();
    });
});
