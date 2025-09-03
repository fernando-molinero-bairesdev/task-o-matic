# Task-O-Matic Monorepo

This is a monorepository for a task management system with:
- **Backend**: FastAPI, PostgreSQL, Redis (token caching)
- **Frontend**: React

## Structure
- `backend/` — FastAPI app, PostgreSQL models, Redis integration
- `frontend/` — React app

## Setup

### 1. Git Setup
- Monorepo with separate `.gitignore` for backend, frontend, and root
- Run `git init` in the root directory

### 2. Backend
- Python 3.10+
- Install dependencies: `pip install fastapi[all] psycopg2-binary redis`
- Configure PostgreSQL and Redis in `.env`

### 3. Frontend
- Node.js 18+
- Install dependencies: `npm install` (after scaffolding)

### 4. Development
- Backend: `uvicorn main:app --reload`
- Frontend: `npm start`

---

Replace placeholder code with your implementation as you build out features.
