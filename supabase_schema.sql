-- AI Career Companion - Supabase Database Schema
-- Run this in Supabase SQL Editor to create all tables

-- ============================================
-- PROFILES TABLE
-- Stores user profile data (Digital Twin)
-- ============================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT,
    email TEXT,
    github_username TEXT,
    linkedin_url TEXT,
    skills JSONB DEFAULT '[]'::jsonb,
    experience JSONB DEFAULT '[]'::jsonb,
    education JSONB DEFAULT '[]'::jsonb,
    career_goals JSONB DEFAULT '[]'::jsonb,
    resume_text TEXT,
    github_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own profile
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);


-- ============================================
-- APPLICATIONS TABLE
-- Tracks job applications
-- ============================================
CREATE TABLE IF NOT EXISTS applications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_title TEXT NOT NULL,
    company TEXT NOT NULL,
    job_url TEXT,
    status TEXT DEFAULT 'applied' CHECK (status IN ('applied', 'viewed', 'interview', 'offer', 'rejected')),
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT,
    resume_version TEXT,
    cover_letter TEXT
);

-- Enable Row Level Security
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own applications" ON applications;
CREATE POLICY "Users can view own applications" ON applications
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own applications" ON applications;
CREATE POLICY "Users can insert own applications" ON applications
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own applications" ON applications;
CREATE POLICY "Users can update own applications" ON applications
    FOR UPDATE USING (auth.uid() = user_id);


-- ============================================
-- LEARNING_PROGRESS TABLE
-- Tracks roadmap/learning progress
-- ============================================
CREATE TABLE IF NOT EXISTS learning_progress (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    roadmap_id TEXT,
    milestone_id TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    time_spent_minutes INTEGER DEFAULT 0,
    notes TEXT,
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, milestone_id)
);

-- Enable Row Level Security
ALTER TABLE learning_progress ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own progress" ON learning_progress;
CREATE POLICY "Users can view own progress" ON learning_progress
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own progress" ON learning_progress;
CREATE POLICY "Users can insert own progress" ON learning_progress
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own progress" ON learning_progress;
CREATE POLICY "Users can update own progress" ON learning_progress
    FOR UPDATE USING (auth.uid() = user_id);


-- ============================================
-- WELLNESS_LOGS TABLE
-- Tracks wellness/burnout data
-- ============================================
CREATE TABLE IF NOT EXISTS wellness_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    mood TEXT CHECK (mood IN ('great', 'good', 'neutral', 'low', 'struggling')),
    energy_level INTEGER CHECK (energy_level BETWEEN 1 AND 10),
    sleep_hours DECIMAL(3,1),
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10),
    notes TEXT,
    logged_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE wellness_logs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own wellness logs" ON wellness_logs;
CREATE POLICY "Users can view own wellness logs" ON wellness_logs
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own wellness logs" ON wellness_logs;
CREATE POLICY "Users can insert own wellness logs" ON wellness_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);


-- ============================================
-- SAVED_JOBS TABLE
-- Jobs saved for later
-- ============================================
CREATE TABLE IF NOT EXISTS saved_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    job_url TEXT,
    salary TEXT,
    skills_required JSONB DEFAULT '[]'::jsonb,
    match_score DECIMAL(5,2),
    source_platform TEXT,
    saved_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE saved_jobs ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own saved jobs" ON saved_jobs;
CREATE POLICY "Users can view own saved jobs" ON saved_jobs
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own saved jobs" ON saved_jobs;
CREATE POLICY "Users can insert own saved jobs" ON saved_jobs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own saved jobs" ON saved_jobs;
CREATE POLICY "Users can delete own saved jobs" ON saved_jobs
    FOR DELETE USING (auth.uid() = user_id);


-- ============================================
-- INTERVIEW_SESSIONS TABLE
-- Mock interview history
-- ============================================
CREATE TABLE IF NOT EXISTS interview_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    job_title TEXT,
    company TEXT,
    interview_type TEXT CHECK (interview_type IN ('behavioral', 'technical', 'hr', 'case')),
    questions JSONB DEFAULT '[]'::jsonb,
    answers JSONB DEFAULT '[]'::jsonb,
    scores JSONB DEFAULT '[]'::jsonb,
    overall_score DECIMAL(3,1),
    feedback TEXT,
    conducted_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE interview_sessions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own interviews" ON interview_sessions;
CREATE POLICY "Users can view own interviews" ON interview_sessions
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own interviews" ON interview_sessions;
CREATE POLICY "Users can insert own interviews" ON interview_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);


-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_user_id ON applications(user_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_learning_progress_user_id ON learning_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_wellness_logs_user_id ON wellness_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_wellness_logs_logged_at ON wellness_logs(logged_at);
CREATE INDEX IF NOT EXISTS idx_saved_jobs_user_id ON saved_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_interview_sessions_user_id ON interview_sessions(user_id);


-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to get application stats for a user
CREATE OR REPLACE FUNCTION get_application_stats(p_user_id UUID)
RETURNS TABLE (
    total INTEGER,
    applied INTEGER,
    interviews INTEGER,
    offers INTEGER,
    rejected INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::INTEGER as total,
        COUNT(*) FILTER (WHERE status = 'applied')::INTEGER as applied,
        COUNT(*) FILTER (WHERE status = 'interview')::INTEGER as interviews,
        COUNT(*) FILTER (WHERE status = 'offer')::INTEGER as offers,
        COUNT(*) FILTER (WHERE status = 'rejected')::INTEGER as rejected
    FROM applications
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;


-- Function to get learning streak
CREATE OR REPLACE FUNCTION get_learning_streak(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
    streak INTEGER := 0;
    check_date DATE := CURRENT_DATE;
    has_activity BOOLEAN;
BEGIN
    LOOP
        SELECT EXISTS (
            SELECT 1 FROM learning_progress
            WHERE user_id = p_user_id
            AND updated_at::DATE = check_date
            AND completed = TRUE
        ) INTO has_activity;
        
        EXIT WHEN NOT has_activity;
        
        streak := streak + 1;
        check_date := check_date - INTERVAL '1 day';
    END LOOP;
    
    RETURN streak;
END;
$$ LANGUAGE plpgsql;


-- ============================================
-- TRIGGERS (AUTOMATIC PROFILE CREATION)
-- ============================================

-- 1. Create a function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER SET search_path = public
AS $$
BEGIN
  INSERT INTO public.profiles (user_id, email, name)
  VALUES (
    new.id, 
    new.email, 
    new.raw_user_meta_data ->> 'name'
  );
  RETURN new;
END;
$$;

-- 2. Create the trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
