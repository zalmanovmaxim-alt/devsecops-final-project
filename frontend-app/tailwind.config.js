/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'bg-page': '#0b1220',
                'bg-surface': '#111827',
                'bg-surface-2': '#0f172a',
                'text-primary': '#e5e7eb',
                'text-secondary': '#cbd5e1',
                'matte-blue': '#345da7',
                'matte-blue-hover': '#2a4a86',
            }
        },
    },
    plugins: [],
}
