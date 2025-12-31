import React, { useState, useEffect } from 'react';
import { Screen } from '../../types';
import Button from '../ui/Button';
import GlassCard from '../ui/GlassCard';

interface OnboardingFlowProps {
  currentStep: Screen;
  onNavigate: (screen: Screen) => void;
}

// --- Sub-components for Steps to prevent layout thrashing and re-renders ---

import { auth, onboarding } from '../../services/api';

const Step1 = ({ onNavigate }: { onNavigate: (s: Screen) => void }) => {
  const [isLogin, setIsLogin] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [github, setGithub] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        // Login Logic
        console.log('Attempting login with:', { email });
        const res = await auth.signin({ email, password });
        if (res.data.access_token) {
          localStorage.setItem('access_token', res.data.access_token);
          localStorage.setItem('user', JSON.stringify(res.data.user));
          // Check if profile exists to decide where to go, but for now go to Dashboard
          // Ideally we should check if onboarding is complete.
          // Let's assume if they login, they go to Dashboard.
          onNavigate(Screen.DASHBOARD);
        }
      } else {
        // Signup Logic
        console.log('Attempting signup with:', { email, name, github });
        const res = await auth.signup({ email, password, name });

        if (res.data.success) {
          try {
            const signInRes = await auth.signin({ email, password });
            if (signInRes.data.access_token) {
              localStorage.setItem('access_token', signInRes.data.access_token);
              localStorage.setItem('user', JSON.stringify(signInRes.data.user));
              if (github) {
                localStorage.setItem('github_username', github);
              }
              onNavigate(Screen.ONBOARDING_2);
            }
          } catch (signInErr: any) {
            // Likely needs email verification
            alert("Account created! Please check your email to verify your account before logging in.");
            setIsLogin(true); // Switch to login mode
          }
        }
      }
    } catch (err: any) {
      console.error('Auth error:', err);
      const msg = err.response?.data?.detail || err.message || 'Authentication failed';
      if (msg.includes('security purposes')) {
        setError('Too many attempts. Please wait a minute or check your email for verification.');
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-[1000px] glass-panel rounded-2xl overflow-hidden flex flex-col md:flex-row min-h-0 md:min-h-[580px] animate-fade-up shadow-2xl">
      {/* Left visual side */}
      <div className="w-full md:w-5/12 relative bg-[#0f1623]/50 border-b md:border-b-0 md:border-r border-white/5 p-8 md:p-12 flex flex-col items-center justify-center overflow-hidden min-h-[300px]">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200px] h-[200px] bg-primary/20 blur-[80px] rounded-full pointer-events-none"></div>
        <div className="relative z-10 w-full max-w-[240px] aspect-square flex items-center justify-center animate-float">
          <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCXkIB8NpfPZnHyhiM4BMWMXo1UPilc7TI20eUUcEy8zo_lSalF8kh6lw0JCgwF58lqwC4pv9PdX2IlRHOdZ92dOtnY8Iw7iCO8mlJrtw9AqRoNxNmu1f6odVh-_BVmyTJPMezRhWxE42QT5MeSQtTvOHx30rvum66TlAWbjTGVIV3IX-fT-MlxbBuje9O460Urv-V5-_YwrA_vJxCnyExOxG5WUC39f-8FHwZ4Zd068hqfHJvW-pO9YxyTbIJ9DN5Yf5IdxpxWAzY" className="w-full h-full object-contain drop-shadow-[0_20px_40px_rgba(0,0,0,0.5)]" alt="Robot Mascot" />
        </div>
        <div className="relative z-10 mt-6 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-semibold tracking-wide uppercase">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            System Online
          </div>
        </div>
      </div>
      {/* Right Form Side */}
      <div className="w-full md:w-7/12 p-6 md:p-12 flex flex-col justify-center">
        <div className="mb-8">
          <div className="flex justify-between items-end mb-2">
            <p className="text-white text-sm font-medium">{isLogin ? 'Welcome Back' : 'Step 1 of 4'}</p>
            {!isLogin && <p className="text-slate-400 text-xs font-normal">25% Complete</p>}
          </div>
          {!isLogin && (
            <div className="w-full rounded-full bg-[#1e293b] h-1.5 overflow-hidden">
              <div className="h-full rounded-full bg-gradient-to-r from-primary to-primary-dark shadow-[0_0_10px_#00CED1]" style={{ width: '25%' }}></div>
            </div>
          )}
        </div>

        <div className="mb-8">
          <h1 className="text-white text-3xl md:text-4xl font-bold leading-tight mb-3">
            {isLogin ? 'Welcome back,' : "Let's build your"} <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent-cyan" style={{ textShadow: '0 0 20px rgba(0, 255, 255, 0.3)' }}>{isLogin ? 'Commander' : 'Digital Twin'}</span> {isLogin ? '🚀' : '🧬'}
          </h1>
          <p className="text-[#90a7cb] text-sm md:text-base">{isLogin ? 'Enter your credentials to access mission control.' : 'First, we need to know who you are to start training your personal AI career coach.'}</p>
        </div>

        <form className="flex flex-col gap-5 w-full" onSubmit={handleAuth}>
          {error && <div className="text-red-400 text-sm bg-red-500/10 p-3 rounded-lg border border-red-500/20">{error}</div>}

          {!isLogin && (
            <div className="space-y-2">
              <label className="text-white text-sm font-medium ml-1">Full Name</label>
              <div className="relative group focus-within:shadow-[0_0_15px_rgba(0,206,209,0.3)] rounded-xl transition-all duration-300">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <span className="material-symbols-outlined text-[#90a7cb] group-focus-within:text-primary">person</span>
                </div>
                <input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Alex Chen" className="w-full bg-[#182334]/50 border border-[#314668] rounded-xl pl-12 py-3.5 text-white placeholder:text-[#90a7cb]/50 focus:border-primary focus:ring-0 transition-colors" required={!isLogin} />
              </div>
            </div>
          )}

          <div className="space-y-2">
            <label className="text-white text-sm font-medium ml-1">Work Email</label>
            <div className="relative group focus-within:shadow-[0_0_15px_rgba(0,206,209,0.3)] rounded-xl transition-all duration-300">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <span className="material-symbols-outlined text-[#90a7cb] group-focus-within:text-primary">mail</span>
              </div>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="alex@company.com" className="w-full bg-[#182334]/50 border border-[#314668] rounded-xl pl-12 py-3.5 text-white placeholder:text-[#90a7cb]/50 focus:border-primary focus:ring-0 transition-colors" required />
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-white text-sm font-medium ml-1">Password</label>
            <div className="relative group focus-within:shadow-[0_0_15px_rgba(0,206,209,0.3)] rounded-xl transition-all duration-300">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <span className="material-symbols-outlined text-[#90a7cb] group-focus-within:text-primary">lock</span>
              </div>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" className="w-full bg-[#182334]/50 border border-[#314668] rounded-xl pl-12 py-3.5 text-white placeholder:text-[#90a7cb]/50 focus:border-primary focus:ring-0 transition-colors" required />
            </div>
          </div>

          {!isLogin && (
            <div className="space-y-2">
              <label className="text-white text-sm font-medium ml-1">GitHub Username (Optional)</label>
              <div className="relative group focus-within:shadow-[0_0_15px_rgba(0,206,209,0.3)] rounded-xl transition-all duration-300">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <span className="material-symbols-outlined text-[#90a7cb] group-focus-within:text-primary">code</span>
                </div>
                <input type="text" value={github} onChange={e => setGithub(e.target.value)} placeholder="octocat" className="w-full bg-[#182334]/50 border border-[#314668] rounded-xl pl-12 py-3.5 text-white placeholder:text-[#90a7cb]/50 focus:border-primary focus:ring-0 transition-colors" />
              </div>
            </div>
          )}

          <div className="mt-4 flex flex-col gap-4">
            <Button type="submit" icon="arrow_forward" className="w-full" disabled={loading}>{loading ? (isLogin ? 'Logging in...' : 'Creating Account...') : (isLogin ? 'Login' : 'Next Step')}</Button>

            <div className="flex justify-center">
              <button type="button" onClick={() => { setIsLogin(!isLogin); setError(''); }} className="text-slate-400 hover:text-white text-sm transition-colors">
                {isLogin ? "Don't have an account? Sign up" : "Already have an account? Login"}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

const Step2 = ({ onNavigate, renderProgressBar }: { onNavigate: (s: Screen) => void, renderProgressBar: (n: number) => React.ReactNode }) => {
  const [uploading, setUploading] = useState(false);
  const [skills, setSkills] = useState<string[]>([]);
  const [analyzing, setAnalyzing] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setUploading(true);
      setAnalyzing(true);

      const formData = new FormData();
      formData.append('file', file);

      try {
        // Use the onboarding service
        // We use analyzeResume to just get skills without creating a full profile yet if we want
        // OR uploadResume if we want to attach it to the current user.
        // Since we are authenticated (or should be), let's use uploadResume but we might need to handle the response.
        // Actually, let's use analyzeResume first to show the "Skills Detected" animation.

        // Note: In a real app, we'd probably want to upload it to the profile.
        // Let's assume we are authenticated from Step 1.
        const res = await onboarding.analyzeResume(formData);
        if (res.data && res.data.profile && res.data.profile.skills) {
          // Extract skills from the response
          // The response structure depends on DigitalTwinAgent.
          // It likely returns { profile: { skills: [...] } }
          setSkills(res.data.profile.skills.map((s: any) => typeof s === 'string' ? s : s.name).slice(0, 5));
        }
      } catch (error) {
        console.error("Resume upload failed", error);
        alert("Failed to analyze resume. Please try again.");
      } finally {
        setUploading(false);
        setAnalyzing(false);
      }
    }
  };

  return (
    <div className="w-full max-w-3xl flex flex-col gap-8 animate-fade-up px-2">
      <div className="glass-panel rounded-xl p-4 flex flex-col gap-3">
        {renderProgressBar(2)}
      </div>

      <GlassCard className="p-6 md:p-10 flex flex-col gap-8 relative overflow-hidden group">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-transparent via-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>

        <div className="text-center space-y-2 relative z-10">
          <h1 className="text-3xl md:text-4xl font-bold text-white tracking-tight">Let's get to know you</h1>
          <p className="text-slate-400 text-base md:text-lg max-w-xl mx-auto font-light">Upload your resume PDF to let our AI extract your skills and build your profile instantly.</p>
        </div>

        <div className="relative group cursor-pointer z-10">
          <input type="file" accept=".pdf" onChange={handleFileUpload} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20" />
          <div className="absolute -inset-0.5 bg-gradient-to-r from-primary to-primary-dark rounded-xl blur opacity-20 group-hover:opacity-75 transition duration-500"></div>
          <div className="relative flex flex-col items-center justify-center gap-6 rounded-xl border-2 border-dashed border-slate-600 bg-[#131b2c] p-8 md:p-10 transition-all duration-300 group-hover:border-primary/50 group-hover:bg-[#162032]">
            <div className="relative">
              <div className={`size-20 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 group-hover:shadow-[0_0_15px_rgba(0,206,209,0.4)] transition-all duration-300 ${analyzing ? 'animate-pulse' : ''}`}>
                <span className="material-symbols-outlined text-4xl">{analyzing ? 'settings_suggest' : 'cloud_upload'}</span>
              </div>
            </div>
            <div className="text-center space-y-1">
              <p className="text-white text-lg font-semibold group-hover:text-primary transition-colors">{analyzing ? 'Analyzing Resume...' : 'Drop your resume PDF here'}</p>
              <p className="text-slate-500 text-sm">or click to browse files (Max 5MB)</p>
            </div>
            <button className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white px-5 py-2.5 rounded-lg border border-slate-600 transition-all text-sm font-medium">
              <span className="material-symbols-outlined text-[18px]">folder_open</span> Select File
            </button>
          </div>
        </div>

        <div className="flex flex-col gap-3 relative z-10">
          <div className="flex items-center justify-between border-b border-white/5 pb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Skills Detected</span>
            <span className="text-xs text-slate-600">{skills.length > 0 ? `${skills.length} found` : 'Waiting for upload...'}</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {skills.length > 0 ? (
              skills.map((skill, i) => (
                <div key={i} className="px-3 py-1 rounded-full bg-primary/20 border border-primary/30 text-primary text-sm animate-fade-up" style={{ animationDelay: `${i * 100}ms` }}>
                  {skill}
                </div>
              ))
            ) : (
              [1, 2, 3].map(i => <div key={i} className="h-8 w-24 rounded-full bg-slate-800/50 border border-white/5 animate-pulse" style={{ animationDelay: `${i * 100}ms` }}></div>)
            )}
          </div>
        </div>

        <div className="flex items-center justify-between pt-4">
          <button onClick={() => onNavigate(Screen.ONBOARDING_1)} className="text-slate-400 hover:text-white transition-colors text-sm font-medium flex items-center gap-2">
            <span className="material-symbols-outlined text-lg">arrow_back</span> Back
          </button>
          <Button onClick={() => onNavigate(Screen.ONBOARDING_3)} icon="arrow_forward" disabled={uploading}>Continue</Button>
        </div>
      </GlassCard>
    </div>
  );
};

const Step3 = ({ onNavigate, renderProgressBar }: { onNavigate: (s: Screen) => void, renderProgressBar: (n: number) => React.ReactNode }) => {
  const [analyzing, setAnalyzing] = useState(false);
  const [data, setData] = useState<any>(null);
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const storedUsername = localStorage.getItem('github_username');
    if (storedUsername) {
      setUsername(storedUsername);
      handleScan(storedUsername);
    }
  }, []);

  const handleScan = async (user: string) => {
    setAnalyzing(true);
    setError(''); // Clear previous errors
    try {
      const res = await onboarding.analyzeGithub(user);
      if (res.data) {
        setData(res.data);
      }
    } catch (err: any) { // Changed 'error' to 'err' to match the snippet
      console.error("GitHub analysis failed", err);
      if (err.response) {
        console.error('Error response:', err.response.data);
        console.error('Error status:', err.response.status);
        setError(err.response.data.detail || 'Failed to analyze GitHub. Please check the username.');
      } else {
        setError(err.message || 'Network error. Please try again.');
      }
    } finally {
      setAnalyzing(false); // Changed 'setLoading' to 'setAnalyzing'
    }
  };

  return (
    <div className="w-full max-w-4xl flex flex-col items-center justify-center p-4 z-10 animate-fade-up">
      <div className="w-full max-w-md mb-8">
        {renderProgressBar(3)}
      </div>

      <GlassCard className="w-full rounded-2xl p-6 md:p-12 relative overflow-hidden shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/40 pointer-events-none"></div>

        <div className="relative z-10 flex flex-col items-center">
          {/* Visualization */}
          <div className="relative w-full h-64 md:h-80 mb-8 flex items-center justify-center">
            {/* Grid Lines */}
            <div className="absolute w-full max-w-[500px] h-[1px] bg-gradient-to-r from-transparent via-primary/30 to-transparent top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute h-full max-h-[200px] w-[1px] bg-gradient-to-b from-transparent via-primary/30 to-transparent top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"></div>

            {/* Central Hub */}
            <div className="relative z-20 flex flex-col items-center justify-center">
              <div className={`w-24 h-24 rounded-full bg-slate-900 border border-primary/50 shadow-[0_0_40px_-10px_rgba(0,206,209,0.5)] flex items-center justify-center relative group ${analyzing ? 'animate-spin' : ''}`}>
                <div className="absolute inset-0 rounded-full bg-primary/20 blur-xl animate-pulse"></div>
                <span className="material-symbols-outlined text-white text-5xl relative z-10">hub</span>
                <div className="absolute -bottom-2 bg-emerald-500 text-[10px] font-bold text-black px-2 py-0.5 rounded-full shadow-lg border border-white/20 flex items-center gap-1">
                  <span className="material-symbols-outlined text-[12px]">{analyzing ? 'sync' : 'check'}</span> {analyzing ? 'SCANNING' : 'CONNECTED'}
                </div>
              </div>
            </div>

            {/* Floating Nodes - Hidden on small mobile to prevent overlap */}
            {!analyzing && data && (
              <>
                <div className="hidden sm:block absolute top-4 left-[10%] md:left-[20%] animate-float">
                  <div className="px-4 py-2 bg-slate-800/80 backdrop-blur-md border border-white/10 rounded-xl shadow-lg flex items-center gap-3 transform -rotate-3 hover:scale-105 transition-transform">
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary"><span className="material-symbols-outlined text-lg">folder_open</span></div>
                    <div className="text-left"><div className="text-xs text-slate-400">Projects</div><div className="text-sm font-bold text-white">{data.repositories?.length || 0} Found</div></div>
                  </div>
                </div>
                <div className="hidden sm:block absolute bottom-10 right-[5%] md:right-[20%] animate-float" style={{ animationDelay: '1s' }}>
                  <div className="px-4 py-2 bg-slate-800/80 backdrop-blur-md border border-white/10 rounded-xl shadow-lg flex items-center gap-3 transform rotate-2 hover:scale-105 transition-transform">
                    <div className="w-8 h-8 rounded-full bg-accent-violet/20 flex items-center justify-center text-accent-violet"><span className="material-symbols-outlined text-lg">code</span></div>
                    <div className="text-left"><div className="text-xs text-slate-400">Languages</div><div className="text-sm font-bold text-white">{Object.keys(data.languages || {}).length} Detected</div></div>
                  </div>
                </div>
              </>
            )}
          </div>

          <div className="max-w-2xl text-center space-y-4">
            <h2 className="text-white tracking-tight text-3xl md:text-4xl font-bold leading-tight drop-shadow-lg">
              {analyzing ? (
                <span>Scanning <span className="text-primary">@{username}</span>...</span>
              ) : data ? (
                <span>We found <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent-cyan">{data.repositories?.length || 0} projects</span>! 🎉</span>
              ) : (
                <span>Connect your <span className="text-white">GitHub</span></span>
              )}
            </h2>
            <p className="text-slate-300 text-base md:text-lg font-light leading-relaxed">
              {analyzing ? "Analyzing your repositories to detect skills and coding patterns." : data ? "Excellent! Our AI has analyzed your public repositories and identified your key strengths." : "Enter your username to let us analyze your code."}
            </p>

            {!data && !analyzing && (
              <div className="flex gap-2 justify-center mt-4">
                <input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="GitHub Username" className="bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 text-white" />
                <Button onClick={() => handleScan(username)} disabled={!username}>Scan</Button>
              </div>
            )}
          </div>

          <div className="mt-10 flex flex-col items-center gap-4 w-full">
            <Button size="lg" icon="arrow_forward" onClick={() => onNavigate(Screen.ONBOARDING_4)} disabled={analyzing}>Continue to Analysis</Button>
            <div className="flex items-center gap-2 mt-2">
              <button onClick={() => handleScan(username)} className="text-slate-500 hover:text-slate-300 text-sm font-medium transition-colors flex items-center gap-1"><span className="material-symbols-outlined text-base">refresh</span> Rescan GitHub</button>
              <span className="text-slate-700">•</span>
              <button className="text-slate-500 hover:text-slate-300 text-sm font-medium transition-colors" onClick={() => onNavigate(Screen.ONBOARDING_4)}>Skip for now</button>
            </div>
          </div>
        </div>
      </GlassCard>
    </div>
  );
};

const Step4 = ({ onNavigate, renderProgressBar }: { onNavigate: (s: Screen) => void, renderProgressBar: (n: number) => React.ReactNode }) => {
  const [role, setRole] = useState('');
  const [saving, setSaving] = useState(false);

  const handleContinue = async () => {
    if (!role) return;
    setSaving(true);
    try {
      await auth.updateProfile({
        career_goals: [{ role: role, timeframe: '6 months' }]
      });
      onNavigate(Screen.ONBOARDING_5);
    } catch (error) {
      console.error("Failed to save role", error);
      onNavigate(Screen.ONBOARDING_5);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="w-full max-w-[800px] flex flex-col gap-8 animate-fade-up px-2">
      <div className="w-full max-w-[640px] mb-8 mx-auto">
        {renderProgressBar(4)}
      </div>

      <GlassCard className="p-6 md:p-10 relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/2 pointer-events-none"></div>
        <div className="flex flex-col gap-6 relative z-10">
          <div className="space-y-2">
            <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight leading-tight">
              What role are you <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00FFFF] to-primary" style={{ textShadow: '0 0 10px rgba(0, 206, 209, 0.5)' }}>targeting?</span>
            </h1>
            <p className="text-slate-400 text-lg font-light leading-relaxed max-w-xl">
              Select your dream job so our AI can map the fastest trajectory from your current skills to your goal.
            </p>
          </div>

          <div className="relative w-full max-w-xl z-20">
            <div className="relative group rounded-xl transition-all duration-300 focus-within:shadow-[0_0_15px_rgba(0,206,209,0.3)]">
              <span className="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400"><span className="material-symbols-outlined">search</span></span>
              <input type="text" value={role} onChange={e => setRole(e.target.value)} placeholder="e.g., Senior UX Designer, DevOps Engineer..." className="w-full h-14 pl-12 pr-12 rounded-xl bg-[#182334] border border-slate-700 text-white placeholder:text-slate-500 focus:outline-none focus:ring-0 focus:border-primary/50 text-base font-medium transition-colors" />
              <span className="absolute inset-y-0 right-0 flex items-center pr-4">
                <button className="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"><span className="material-symbols-outlined text-[20px]">mic</span></button>
              </span>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <p className="text-xs text-slate-500 uppercase font-semibold tracking-wider w-full mb-1">Popular Roles</p>
              {['Full Stack Developer', 'Product Manager', 'AI Engineer', 'Data Scientist'].map((role, idx) => (
                <button key={role} onClick={() => setRole(role)} className={`flex items-center gap-2 h-9 px-4 rounded-lg text-sm font-medium transition-all duration-200 ${role === role ? 'bg-primary/20 border border-primary/40 text-white shadow-[0_0_10px_rgba(0,206,209,0.2)]' : 'bg-white/5 border border-white/10 hover:bg-white/10 hover:border-primary/30 hover:text-white text-slate-300'}`}>
                  {role} {idx === 1 && <span className="material-symbols-outlined text-[16px]">check</span>}
                </button>
              ))}
            </div>
          </div>
        </div>
      </GlassCard>

      <div className="bg-primary/10 border border-primary/30 rounded-2xl p-6 md:p-8 flex flex-col md:flex-row gap-8 items-center md:items-start relative overflow-hidden animate-fade-up" style={{ animationDelay: '0.2s' }}>
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-primary via-[#008080] to-transparent"></div>
        <div className="shrink-0 relative size-32 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border-4 border-primary/20"></div>
          <svg className="size-full -rotate-90" viewBox="0 0 100 100">
            <circle cx="50" cy="50" fill="transparent" r="40" stroke="currentColor" strokeWidth="8" strokeDasharray="251.2" strokeDashoffset="70" strokeLinecap="round" className="text-primary"></circle>
          </svg>
          <div className="flex flex-col items-center justify-center text-center absolute inset-0">
            <span className="text-2xl font-bold text-white leading-none">72%</span>
            <span className="text-[10px] text-primary uppercase font-bold tracking-wide mt-1">Match</span>
          </div>
        </div>
        <div className="flex-1 space-y-4 w-full">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">analytics</span> Initial Match Estimate
              </h3>
              <p className="text-slate-400 text-sm mt-1">Target: <span className="text-white font-medium">Product Manager</span></p>
            </div>
            <span className="px-2 py-1 rounded bg-primary/20 text-primary text-xs font-bold border border-primary/20">AI ANALYSIS</span>
          </div>
          <p className="text-slate-300 text-sm leading-relaxed">
            Based on your previous inputs, you have strong foundations in <span className="text-white border-b border-white/20">Engineering</span> and <span className="text-white border-b border-white/20">Agile</span>, but may need to boost <span className="text-primary font-medium">Strategic Planning</span> skills.
          </p>
        </div>
      </div>

      <div className="w-full flex items-center justify-between mt-4">
        <button onClick={() => onNavigate(Screen.ONBOARDING_3)} className="group flex items-center gap-2 px-6 py-3 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 transition-all">
          <span className="material-symbols-outlined text-[20px] transition-transform group-hover:-translate-x-1">arrow_back</span> Back
        </button>
        <Button icon="arrow_forward" onClick={handleContinue} disabled={!role || saving}>{saving ? 'Saving...' : 'Continue'}</Button>
      </div>
    </div>
  );
};

const Step5 = ({ onNavigate }: { onNavigate: (s: Screen) => void }) => (
  <div className="w-full max-w-5xl flex flex-col gap-8 animate-fade-up px-2">
    <div className="relative w-full bg-white/60 dark:bg-[#1A2333]/60 backdrop-blur-xl border border-white/20 rounded-2xl md:rounded-3xl shadow-2xl p-8 md:p-12 overflow-hidden">
      <div className="absolute top-10 left-10 text-yellow-400 opacity-60 transform -rotate-12"><span className="material-symbols-outlined text-3xl">star</span></div>
      <div className="absolute bottom-20 right-10 text-primary opacity-50 transform rotate-45"><span className="material-symbols-outlined text-2xl">celebration</span></div>

      <div className="relative flex flex-col md:flex-row items-center gap-10 md:gap-16">
        <div className="flex-shrink-0 relative">
          <div className="absolute inset-0 bg-primary/20 rounded-full blur-3xl transform scale-110"></div>
          <div className="relative size-56 md:size-64">
            <svg className="size-full -rotate-90 transform" viewBox="0 0 100 100">
              <circle className="text-slate-200 dark:text-[#2a3855]" cx="50" cy="50" fill="none" r="42" stroke="currentColor" strokeWidth="6"></circle>
              <circle className="drop-shadow-[0_0_10px_rgba(0,206,209,0.6)]" cx="50" cy="50" fill="none" r="42" stroke="#00CED1" strokeDasharray="264" strokeDashoffset="0" strokeLinecap="round" strokeWidth="6"></circle>
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <div className="mb-2 p-3 bg-primary/10 rounded-full text-primary shadow-[0_0_15px_rgba(0,206,209,0.3)]">
                <span className="material-symbols-outlined text-4xl">check_circle</span>
              </div>
              <span className="text-4xl font-black text-white tracking-tight">100%</span>
              <span className="text-xs uppercase tracking-widest font-semibold text-slate-400 mt-1">Complete</span>
            </div>
          </div>
        </div>

        <div className="flex flex-col items-center md:items-start text-center md:text-left flex-1 space-y-6">
          <div className="space-y-2">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-white tracking-tighter leading-tight">
              All Set! <br /> <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-[#00CED1] to-accent-violet">Ready for Liftoff.</span>
            </h1>
            <p className="text-lg md:text-xl text-slate-300 font-light max-w-lg leading-relaxed">We've analyzed your profile and tailored your career path. Your personalized dashboard is unlocked and ready to explore.</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto pt-2">
            <Button size="lg" icon="rocket_launch" onClick={() => onNavigate(Screen.DASHBOARD)}>Launch Dashboard</Button>
            <button className="flex items-center justify-center gap-2 h-14 px-8 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 text-white text-base font-semibold transition-all">View Profile</button>
          </div>
        </div>
      </div>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
      {[
        { icon: 'description', title: 'AI Resume Scan', desc: 'Deep analysis of your CV strengths.', status: 'Unlocked', statusColor: 'emerald', bgIcon: 'description' },
        { icon: 'bolt', title: 'Smart Job Match', desc: 'Roles tailored to your unique skills.', status: 'Active', statusColor: 'cyan', bgIcon: 'work' },
        { icon: 'auto_awesome', title: 'Skill Gap Analysis', desc: 'Personalized learning path generated.', status: 'Ready', statusColor: 'purple', bgIcon: 'analytics' }
      ].map((item, idx) => (
        <div key={idx} className="group relative flex flex-col p-6 rounded-xl bg-[#1A2333]/40 border border-white/5 backdrop-blur-md overflow-hidden hover:bg-[#1A2333]/60 transition-colors">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity"><span className="material-symbols-outlined text-6xl text-primary">{item.bgIcon}</span></div>
          <div className="flex items-center gap-3 mb-4">
            <div className={`p-2 rounded-lg bg-${item.statusColor}-500/10 text-${item.statusColor}-500`}><span className="material-symbols-outlined">{item.icon}</span></div>
            <span className={`text-sm font-semibold text-${item.statusColor}-400 uppercase tracking-wider`}>{item.status}</span>
          </div>
          <h3 className="text-lg font-bold text-white mb-1">{item.title}</h3>
          <p className="text-sm text-slate-400">{item.desc}</p>
        </div>
      ))}
    </div>
  </div>
);

const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ currentStep, onNavigate }) => {
  // Simulate loader state for Step 3
  const [scanning, setScanning] = useState(false);

  useEffect(() => {
    if (currentStep === Screen.ONBOARDING_3) {
      setScanning(true);
      const timer = setTimeout(() => setScanning(false), 2000); // Simulate scan
      return () => clearTimeout(timer);
    }
  }, [currentStep]);

  const renderProgressBar = (step: number) => {
    const percentage = step * 20; // 5 steps total
    return (
      <div className="w-full mb-8">
        <div className="flex justify-between items-end mb-2">
          <span className="text-white text-sm font-medium">Step {step} of 5</span>
          <span className="text-primary text-xs font-bold uppercase tracking-wider">{step === 3 && scanning ? 'ANALYZING...' : `${percentage}% Complete`}</span>
        </div>
        <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-primary-dark to-primary shadow-[0_0_10px_rgba(0,206,209,0.6)] transition-all duration-1000" style={{ width: `${percentage}%` }}></div>
        </div>
      </div>
    );
  };

  const renderHeader = () => (
    <header className="absolute top-0 w-full p-6 flex justify-between items-center z-20">
      <div className="flex items-center gap-2 cursor-pointer" onClick={() => onNavigate(Screen.LANDING)}>
        <span className="material-symbols-outlined text-primary text-3xl">smart_toy</span>
        <span className="font-bold text-lg tracking-tight text-white/90">Career<span className="text-primary">AI</span></span>
      </div>
      <button className="text-sm font-medium text-slate-400 hover:text-white transition-colors flex items-center gap-1">
        <span className="material-symbols-outlined text-[18px]">help</span> Help
      </button>
    </header>
  );

  return (
    <div className="relative min-h-screen flex flex-col items-center pt-24 pb-10 px-4">
      {renderHeader()}
      {currentStep === Screen.ONBOARDING_1 && <Step1 onNavigate={onNavigate} />}
      {currentStep === Screen.ONBOARDING_2 && <Step2 onNavigate={onNavigate} renderProgressBar={renderProgressBar} />}
      {currentStep === Screen.ONBOARDING_3 && <Step3 onNavigate={onNavigate} renderProgressBar={renderProgressBar} />}
      {currentStep === Screen.ONBOARDING_4 && <Step4 onNavigate={onNavigate} renderProgressBar={renderProgressBar} />}
      {currentStep === Screen.ONBOARDING_5 && <Step5 onNavigate={onNavigate} />}
    </div>
  );
};

export default OnboardingFlow;