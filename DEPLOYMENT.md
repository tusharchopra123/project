# Deployment Guide: WealthTrack

## 1. Hosting Architecture
*   **Frontend (Next.js)**: Host on **Vercel** (Free Tier).
*   **Backend (FastAPI)**: Host on **Render** (Free Tier) or **Railway** (Trial).
*   **Database (Postgres)**: Host on **Neon.tech** (Free Tier) - *Recommended for Render compatibility*.

---

## 2. Backend Deployment (Render.com)

1.  **Push to GitHub**: Make sure your code is in a GitHub repository.
2.  **Create New Web Service**:
    *   Go to dashboard.render.com -> "New" -> "Web Service".
    *   Connect your GitHub Repo.
3.  **Configure Settings**:
    *   **Root Directory**: `backend` (Important! Since your app is in a subfolder).
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
        > [!IMPORTANT]
        > Ensure you use `--port` and NOT `-p`. Uvicorn does not support the shorthand `-p` flag.
4.  **Environment Variables** (Add these in the "Environment" tab):
    *   `PYTHON_VERSION`: `3.11.0` (Recommended)
    *   `DATABASE_URL`: `postgresql://[user]:[password]@[host]/neondb?sslmode=require`
        > [!NOTE]
        > **Neon.tech** is recommended because its free tier supports IPv4, which is required by Render.
    *   `GOOGLE_CLIENT_ID`: (Your Google Client ID).
    *   `GOOGLE_CLIENT_SECRET`: (Your Google Client Secret).

---

## 3. Frontend Deployment (Vercel)

1.  **Create New Project**:
    *   Go to vercel.com -> "Add New..." -> "Project".
    *   Import your GitHub Repo.
2.  **Configure Settings**:
    *   **Root Directory**: `frontend` (Important!).
    *   **Framework Preset**: Next.js (Should auto-detect).
3.  **Environment Variables**:
    *   `GOOGLE_CLIENT_ID`: (Same as Backend).
    *   `GOOGLE_CLIENT_SECRET`: (Same as Backend).
    *   `NEXTAUTH_SECRET`: (Generate a random string, e.g., `openssl rand -base64 32`).
    *   `NEXTAUTH_URL`: `https://your-project-name.vercel.app` (The domain Vercel gives you).
    *   `BACKEND_URL`: `https://your-backend-name.onrender.com` (The URL Render gives you).

---

## 4. Final Configuration (Google Cloud)

Once both are deployed:

1.  Go to **Google Cloud Console** -> "APIs & Services" -> "Credentials".
2.  Edit your OAuth 2.0 Client.
3.  **Authorized Javascript Origins**: Add your Frontend URL (`https://your-frontend.vercel.app`).
4.  **Authorized Redirect URIs**: Add your Callback URL (`https://your-frontend.vercel.app/api/auth/callback/google`).

---

## Summary
*   **Locally**: The app runs on `localhost` with SQLite (Database file).
*   **In Cloud**: The app runs on Vercel/Render with Supabase (Cloud Database).
*   The code handles both automatically!

## 5. Troubleshooting

### `OSError: [Errno 101] Network is unreachable` (Database Connection)
This happens because Render (Free Tier) only supports IPv4, while Supabase's free direct connection is IPv6-only. 
**Fix**: Switch to **Neon.tech**. 
1. Create a free account at [neon.tech](https://neon.tech).
2. Create a new project.
3. Copy the **Connection String** (Postgres).
4. Update the `DATABASE_URL` in your Render Environment Variables.
5. Neon supports IPv4 by default, so it works perfectly on Render for free.

### `uvicorn: error: no such option: -p`
This happens if you use `-p` instead of `--port` in the Start Command. Render often defaults to generic commands; ensure you manually set it to `--port 10000`.

### `ModuleNotFoundError: No module named 'sqlalchemy'`
Ensure your `requirements.txt` includes `sqlalchemy`, `aiosqlite`, and `python-dotenv`. If you added them recently, trigger a "Manual Deploy" with "Clear Build Cache" on Render.
