# Deployment Guide: Cricket Simulator

This guide outlines how to deploy your **PRANAV SIMULATOR** so that others can play it online.

## Prerequisites
- A **GitHub** account.
- A **Vercel** account (for the Frontend).
- A **Render** account (for the Backend and Database).

---

## 1. Prepare Your Code (Push to GitHub)

1. Create a new repository on GitHub.
2. Push your entire project folder to this repository.
   ```bash
   git init
   git add .
   git commit -m "Initial commit for deployment"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

---

## 2. Backend Deployment (Render)

### Step A: Create a PostgreSQL Database
1. In your Render Dashboard, click **New +** and select **PostgreSQL**.
2. Name it `cricketsim-db`.
3. After it's created, copy the **Internal Database URL**.

### Step B: Create a Web Service
1. Click **New +** and select **Web Service**.
2. Connect your GitHub repository.
3. **Name**: `cricketsim-backend`.
4. **Root Directory**: `cricketsim_backend`.
5. **Runtime**: `Python`.
6. **Build Command**: 
   ```bash
   pip install -r requirements.txt && python manage.py migrate && python manage.py seed_players
   ```
7. **Start Command**: 
   ```bash
   gunicorn cricketsim.wsgi:application
   ```

### Step C: Environment Variables
Add these under the "Environment" tab in Render:
- `SECRET_KEY`: (Any long random string)
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `*` (or your Render URL)
- `DATABASE_URL`: (Paste your Internal Database URL here)

---

## 3. Frontend Deployment (Vercel)

1. Go to Vercel and click **Add New** > **Project**.
2. Import your GitHub repository.
3. **Framework Preset**: Next.js.
4. **Root Directory**: `cricketsim_frontend`.
5. **Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: (The URL of your Render backend, e.g., `https://cricketsim-backend.onrender.com`)

---

## 4. Final Verification
1. Wait for both deployments to finish.
2. Open your Vercel URL.
3. Start a simulation!

> [!TIP]
> **Free Tier Sleep**: On Render's free tier, the backend "sleeps" after 15 minutes of inactivity. The first time you open the app, it might take ~30 seconds for the backend to wake up.
