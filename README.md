# 🚀 AI Career Companion (AI_VERSE)

> **Agentic AI Career Development Assistant**
> 
> From Confusion to Clarity — An AI That Thinks, Plans, Acts, and Evolves With You. AI_VERSE is a comprehensive platform designed to guide students and professionals through their career journey using a multi-agent AI architecture.

## 🌟 Key Features

- **Digital Twin** — Analyzes your Resume and GitHub to build a dynamic professional profile.
- **Market Oracle** — Scans 40+ Indian job platforms (Naukri, LinkedIn, Internshala, etc.) to find the best matches.
- **Roadmap Architect** — Generates personalized 10-week learning paths with daily micro-tasks.
- **Action Agent** — Tailors your resume for specific JDs and generates ATS-optimized cover letters.
- **Evolution Loop** — Conducts AI-powered mock interviews and analyzes rejections to help you improve.
- **Go Beyond** — Monitors wellness and burnout, providing motivation and mental health checks.
- **Orchestrator** — The "brain" that coordinates all agents to provide a seamless experience.

## 🛠️ Tech Stack

- **Frontend:** React 19, Vite, Tailwind CSS, Framer Motion, Lucide React
- **Backend:** FastAPI (Python 3.11+), LangGraph, Google Gemini Pro
- **Database:** Supabase (PostgreSQL)
- **Search/Scraping:** SearXNG, Crawl4AI, Playwright

## 📂 Project Structure

```text
AI_VERSE/
├── app/                # FastAPI Backend
│   ├── agents/         # Multi-agent logic (Digital Twin, Market Oracle, etc.)
│   ├── models/         # Pydantic models
│   ├── routers/        # API endpoints
│   ├── services/       # External services (LLM, Supabase, GitHub)
│   └── main.py         # Backend entry point
├── ui/                 # React Frontend
│   ├── components/     # UI Components
│   ├── services/       # API integration
│   └── App.tsx         # Frontend entry point
├── supabase_schema.sql # Database schema
├── docker-compose.yml  # SearXNG setup
└── requirements.txt    # Python dependencies
```

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase Account
- Google Gemini API Key

### 2. Backend Setup
```bash
# Navigate to root
cd AI_VERSE

# Install dependencies
pip install -r requirements.txt

# Configure Environment
# Create a .env file in the root directory:
# GOOGLE_API_KEY=your_gemini_key
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_anon_key

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
# Navigate to ui directory
cd ui

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Database Setup
- Create a new project on [Supabase](https://supabase.com/).
- Run the SQL commands from `supabase_schema.sql` in the Supabase SQL Editor.

## 🔄 Workflow & Usage

1. **Onboarding:** Upload your resume and connect your GitHub. The **Digital Twin** agent will analyze your skills.
2. **Job Search:** Paste a Job Description or search for roles. The **Market Oracle** will find matches and provide a readiness score.
3. **Learning:** If there are skill gaps, the **Roadmap Architect** creates a step-by-step learning plan.
4. **Preparation:** Use the **Action Agent** to tailor your resume and the **Evolution Loop** for mock interviews.
5. **Wellness:** Check your dashboard for daily motivation and burnout alerts from the **Go Beyond** agent.

## 🇮🇳 India-Specific Job Support
AI_VERSE is optimized for the Indian market, scraping data from:
- **Jobs:** Naukri, LinkedIn, Indeed, Glassdoor, TimesJobs, Apna
- **Internships:** Internshala, Unstop, LetsIntern
- **Hackathons:** Unstop, Devpost, HackerEarth, Devfolio
- **Courses:** NPTEL, SWAYAM, Coursera, YouTube, GeeksforGeeks

---
Built for the Hackathon - AI Career Companion.
