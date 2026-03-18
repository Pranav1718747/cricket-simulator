# CricketSim AI

A full-stack web application that allows users to create two cricket teams and simulate a 20-over T20 cricket match based on real player statistics.

## Tech Stack
- **Frontend**: Next.js, TailwindCSS, Chart.js
- **Backend & Simulation Engine**: Django, Django REST Framework, Python
- **Database**: SQLite (Pre-seeded with real players)

## Quick Start
The project is split into two folders: `cricketsim_backend` and `cricketsim_frontend`.

### 1. Start the Django Backend
Open a terminal in the project root and run:
```bash
cd cricketsim_backend
source venv/bin/activate
python manage.py runserver 8000
```

### 2. Start the Next.js Frontend
Open a new terminal in the project root and run:
```bash
cd cricketsim_frontend
npm run dev
```

### 3. Usage
Navigate to `http://localhost:3000` in your browser. From there you can:
- **Explore Players**: View the stats and form of the seeded real-world players.
- **Simulator**: Draft exactly 11 players for Team A and Team B, then run the simulation. The backend's probability engine will generate an entire T20 scorecard, live worm charts, and a ball-by-ball analysis.
