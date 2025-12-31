import React, { useEffect, useState } from 'react';
import { Screen } from '../../types';
import GlassCard from '../ui/GlassCard';
import { jobs, wellness, roadmap, auth } from '../../services/api';

interface DashboardProps {
  onNavigate: (screen: Screen) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [trendingSkills, setTrendingSkills] = useState<any[]>([]);
  const [jobMatches, setJobMatches] = useState<any[]>([]);
  const [dailyTasks, setDailyTasks] = useState<any[]>([]);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 1. Get User Profile for matching
        const userRes = await auth.getMe();
        const profile = userRes.data;

        if (profile) {
          setUserProfile(profile.profile || { name: profile.user.email.split('@')[0] }); // Fallback to email name

          // 2. Fetch Job Matches based on profile
          const matchRes = await jobs.match(profile);
          if (matchRes.data && matchRes.data.matches) {
            setJobMatches(matchRes.data.matches.slice(0, 3));
          }
        } else {
          // Fallback mock if no profile yet (shouldn't happen if auth works)
          setJobMatches([
            { title: 'Senior Frontend Engineer', company: 'TechFlow Systems', match: '98%', tags: ['React', 'TypeScript'], logoColor: 'from-accent-violet to-accent-cyan' },
            { title: 'AI Product Designer', company: 'Nebula AI', match: '94%', tags: ['Figma', 'UX Research'], logoColor: 'from-orange-500 to-red-500' },
            { title: 'Full Stack Developer', company: 'Orbit Solutions', match: '88%', tags: ['Node.js', 'Vue'], logoColor: 'from-accent-cyan to-emerald-400' }
          ]);
        }

        // 3. Fetch trending skills
        const skillsRes = await jobs.getTrendingSkills('AI');
        if (skillsRes.data?.trends) {
          setTrendingSkills(skillsRes.data.trends.slice(0, 5));
        }

        // 4. Fetch daily tasks
        const tasksRes = await roadmap.getDailyTasks();
        if (tasksRes.data?.daily_plan?.tasks) {
          setDailyTasks(tasksRes.data.daily_plan.tasks);
        }

      } catch (error) {
        console.error("Failed to fetch dashboard data", error);
        // Keep mock data on error for demo purposes
        setJobMatches([
          { title: 'Senior Frontend Engineer', company: 'TechFlow Systems', match: '98%', tags: ['React', 'TypeScript'], logoColor: 'from-accent-violet to-accent-cyan' },
          { title: 'AI Product Designer', company: 'Nebula AI', match: '94%', tags: ['Figma', 'UX Research'], logoColor: 'from-orange-500 to-red-500' },
          { title: 'Full Stack Developer', company: 'Orbit Solutions', match: '88%', tags: ['Node.js', 'Vue'], logoColor: 'from-accent-cyan to-emerald-400' }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="relative flex flex-col md:flex-row w-full h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-72 h-full glass-panel border-r border-white/10 z-20 shrink-0">
        <div className="flex flex-col h-full p-6 justify-between">
          <div className="flex flex-col gap-8">
            <div className="flex items-center gap-4">
              {/* Avatar removed as per user request */}
              <div className="flex flex-col">
                <h1 className="text-white text-lg font-bold leading-tight tracking-tight">{userProfile?.name || 'Loading...'}</h1>
                <p className="text-slate-400 text-xs font-medium uppercase tracking-wider">Lvl 1 Developer</p>
              </div>
            </div>
            <nav className="flex flex-col gap-2">
              <button onClick={() => onNavigate(Screen.DASHBOARD)} className="flex items-center gap-3 px-4 py-3 rounded-xl bg-primary/20 border border-primary/30 text-white shadow-[0_0_15px_rgba(0,206,209,0.3)] transition-all">
                <span className="material-symbols-outlined text-primary">dashboard</span>
                <p className="text-sm font-semibold">Dashboard</p>
              </button>
              {[
                { label: 'Jobs & Market', icon: 'work', action: () => alert("Jobs & Market module coming soon!") },
                { label: 'Learning Path', icon: 'school', action: () => alert("Learning Path module coming soon!") },
                { label: 'Analyzer', icon: 'description', action: () => onNavigate(Screen.ANALYZER) },
                { label: 'Interviews', icon: 'groups', action: () => alert("Interview module coming soon!") },
                { label: 'Wellness', icon: 'spa', action: () => alert("Wellness module coming soon!") }
              ].map((item) => (
                <button key={item.label} onClick={item.action} className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-slate-400 hover:text-white group">
                  <span className="material-symbols-outlined group-hover:scale-110 transition-transform">{item.icon}</span>
                  <p className="text-sm font-medium">{item.label}</p>
                </button>
              ))}
            </nav>
          </div>
          <div className="flex flex-col gap-2">
            <button className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-all text-slate-400 hover:text-white group">
              <span className="material-symbols-outlined group-hover:rotate-90 transition-transform">settings</span>
              <p className="text-sm font-medium">Settings</p>
            </button>
            <button onClick={() => {
              localStorage.clear();
              window.location.reload();
            }} className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-red-500/10 transition-all text-slate-400 hover:text-red-400 group">
              <span className="material-symbols-outlined">logout</span>
              <p className="text-sm font-medium">Logout</p>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-y-auto bg-[#0B1120] relative">
        {/* Header */}
        <header className="flex items-center justify-between p-6 md:p-8 z-10">
          <div>
            <h2 className="text-2xl font-bold text-white">Welcome back, {userProfile?.name?.split(' ')[0] || 'User'}</h2>
            <p className="text-slate-400 text-sm">Here's your daily career briefing.</p>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors relative">
              <span className="material-symbols-outlined">notifications</span>
              <span className="absolute top-2 right-2 size-2 bg-red-500 rounded-full"></span>
            </button>
            <div className="h-10 w-px bg-white/10 mx-2"></div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-primary/20 to-accent-violet/20 border border-primary/30">
              <span className="material-symbols-outlined text-primary text-sm">bolt</span>
              <span className="text-sm font-bold text-white">850 XP</span>
            </div>
          </div>
        </header>

        <div className="px-6 md:px-8 pb-8 space-y-8 max-w-7xl mx-auto w-full">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { label: 'Profile Strength', value: 'Intermediate', icon: 'fitness_center', color: 'text-orange-400', bg: 'bg-orange-400/10' },
              { label: 'Applications', value: '12 Active', icon: 'send', color: 'text-blue-400', bg: 'bg-blue-400/10' },
              { label: 'Interviews', value: '2 Scheduled', icon: 'calendar_month', color: 'text-purple-400', bg: 'bg-purple-400/10' }
            ].map((stat, idx) => (
              <div key={idx} className="p-5 rounded-2xl bg-[#1A2333]/50 border border-white/5 backdrop-blur-sm flex items-center gap-4">
                <div className={`p-3 rounded-xl ${stat.bg} ${stat.color}`}>
                  <span className="material-symbols-outlined">{stat.icon}</span>
                </div>
                <div>
                  <p className="text-slate-400 text-xs font-medium uppercase tracking-wider">{stat.label}</p>
                  <p className="text-white text-lg font-bold">{stat.value}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column */}
            <div className="lg:col-span-2 space-y-8">
              {/* Job Matches */}
              <section>
                <div className="flex justify-between items-end mb-4">
                  <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary">work</span> Top Job Matches
                  </h3>
                  <button className="text-sm text-primary hover:text-primary-light font-medium">View All</button>
                </div>
                <div className="grid gap-4">
                  {jobMatches.length > 0 ? (
                    jobMatches.map((job, idx) => (
                      <div key={idx} className="group p-5 rounded-2xl bg-[#1A2333] border border-white/5 hover:border-primary/30 transition-all hover:shadow-[0_0_20px_rgba(0,206,209,0.1)] flex items-center gap-5 cursor-pointer">
                        <div className={`size-12 rounded-xl bg-gradient-to-br ${job.logoColor || 'from-slate-700 to-slate-600'} flex items-center justify-center text-white font-bold text-xl`}>
                          {job.company[0]}
                        </div>
                        <div className="flex-1">
                          <h4 className="text-white font-bold text-lg group-hover:text-primary transition-colors">{job.title}</h4>
                          <p className="text-slate-400 text-sm">{job.company} • Remote</p>
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <div className="px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-bold">
                            {job.match} Match
                          </div>
                          <div className="flex gap-1">
                            {job.tags?.slice(0, 2).map((tag: string, i: number) => (
                              <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-white/5 text-slate-400">{tag}</span>
                            ))}
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-8 rounded-2xl bg-[#1A2333]/50 border border-white/5 text-center border-dashed border-slate-700">
                      <span className="material-symbols-outlined text-4xl text-slate-600 mb-2">work_off</span>
                      <p className="text-slate-400 mb-4">No job matches found yet.</p>
                      <button onClick={() => onNavigate(Screen.ANALYZER)} className="px-4 py-2 bg-primary text-black font-bold rounded-lg hover:bg-primary-light transition-colors">
                        Scan Resume to Find Jobs
                      </button>
                    </div>
                  )}
                </div>
              </section>

              {/* Trending Skills */}
              <section>
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <span className="material-symbols-outlined text-accent-violet">trending_up</span> Market Trends
                </h3>
                <div className="p-6 rounded-2xl bg-[#1A2333] border border-white/5">
                  <div className="flex flex-wrap gap-3">
                    {trendingSkills.length > 0 ? (
                      trendingSkills.map((skill, idx) => (
                        <div key={idx} className="px-4 py-2 rounded-xl bg-white/5 border border-white/10 hover:border-accent-violet/50 hover:bg-accent-violet/10 transition-all cursor-default">
                          <div className="flex items-center gap-2">
                            <span className="text-slate-200 font-medium">{skill.name || skill}</span>
                            <span className="text-xs text-green-400 font-bold">+{skill.growth || '12'}%</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-slate-500 text-sm">Loading market trends...</p>
                    )}
                  </div>
                </div>
              </section>
            </div>

            {/* Right Column */}
            <div className="space-y-8">
              {/* Daily Plan */}
              <section className="h-full">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <span className="material-symbols-outlined text-accent-cyan">event_note</span> Daily Plan
                </h3>
                <div className="p-6 rounded-2xl bg-[#1A2333] border border-white/5 h-min">
                  <div className="space-y-4">
                    {dailyTasks.length > 0 ? (
                      dailyTasks.map((task, idx) => (
                        <div key={idx} className="flex gap-4 items-start group">
                          <div className="mt-1 size-5 rounded-md border-2 border-slate-600 group-hover:border-primary cursor-pointer transition-colors"></div>
                          <div>
                            <p className="text-slate-200 font-medium leading-snug group-hover:text-white transition-colors">{task.title || task}</p>
                            <p className="text-xs text-slate-500 mt-1">{task.duration || '15 min'} • {task.type || 'Learning'}</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-6">
                        <p className="text-slate-500 text-sm mb-3">No tasks for today.</p>
                        <button className="text-primary text-sm font-medium hover:underline">Generate Roadmap</button>
                      </div>
                    )}
                  </div>
                  <button className="w-full mt-6 py-3 rounded-xl bg-white/5 hover:bg-white/10 text-white text-sm font-semibold transition-colors flex items-center justify-center gap-2">
                    <span className="material-symbols-outlined text-[18px]">add</span> Add Custom Task
                  </button>
                </div>
              </section>
            </div>
          </div>
        </div>
      </main>
    </div >
  );
};

export default Dashboard;