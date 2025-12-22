# Gamification Frontend (React)

## Overview
This is the modern React frontend for the Gamification Platform, built with Vite and Tailwind CSS.
It replaces the legacy HTML/JS implementation.

## Prerequisites
- Node.js (v18+)
- Docker (optional, for containerization)

## Development Setup
1.  Navigate to the app directory:
    ```bash
    cd react-app
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    Access the app at `http://localhost:8080`.

## Testing
We use [Vitest](https://vitest.dev/) for unit testing.

To run the tests:
```bash
npm test
```
This will execute all test files (e.g., `src/App.test.jsx`) and report results.

## Docker Build
To build the production image (served via Nginx):
```bash
docker build -t frontend-image:latest .
```
Run the container:
```bash
docker run -p 8080:80 frontend-image:latest
```

## Kubernetes
Manifests are located in `../k8s/frontend.yaml`.
