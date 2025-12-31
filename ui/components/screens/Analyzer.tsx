import React, { useState } from 'react';
import { Screen } from '../../types';
import Button from '../ui/Button';
import GlassCard from '../ui/GlassCard';
import { onboarding } from '../../services/api';

interface AnalyzerProps {
   onNavigate: (screen: Screen) => void;
}

const Analyzer: React.FC<AnalyzerProps> = ({ onNavigate }) => {
   const fileInputRef = React.useRef<HTMLInputElement>(null);
   const [analyzing, setAnalyzing] = useState(false);
   const [analysisResult, setAnalysisResult] = useState<any>(null);
   const [error, setError] = useState('');

   const handleUploadClick = () => {
      fileInputRef.current?.click();
   };

   const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      setAnalyzing(true);
      setError('');
      setAnalysisResult(null);

      try {
         const formData = new FormData();
         formData.append('file', file);

         const res = await onboarding.analyzeResume(formData);
         console.log('Analysis result:', res.data);
         setAnalysisResult(res.data);
      } catch (err: any) {
         console.error('Analysis failed:', err);
         const errorMessage = err.response?.data?.detail || 'Failed to analyze resume. Please try again.';
         setError(errorMessage);
      } finally {
         setAnalyzing(false);
      }
   };

   // Helper to parse analysis result or use defaults
   const getScore = () => analysisResult?.readiness_score || 67;
   const getMatchedSkills = () => analysisResult?.skills?.matched || [
      { name: 'React.js', reason: 'Matches core UI library requirement.' },
      { name: 'JavaScript', reason: 'Strong match for DOM & logic needs.' },
      { name: 'CSS/HTML', reason: 'Essential for design implementation.' }
   ];
   const getMissingSkills = () => analysisResult?.skills?.missing || [
      { name: 'TypeScript', desc: 'Adds static types to JS for safety.' },
      { name: 'Redux Toolkit', desc: 'State management for complex apps.' }
   ];

   return (
      <div className="flex flex-col min-h-screen">
         <header className="sticky top-0 z-50 glass-panel border-b border-white/10 px-6 py-4">
            <div className="max-w-7xl mx-auto flex items-center justify-between">
               <div className="flex items-center gap-3 cursor-pointer" onClick={() => onNavigate(Screen.DASHBOARD)}>
                  <div className="size-8 text-primary"><span className="material-symbols-outlined text-3xl">smart_toy</span></div>
                  <h1 className="text-xl font-bold tracking-tight">AI Career Companion</h1>
               </div>
               <nav className="hidden md:flex items-center gap-8">
                  <button onClick={() => onNavigate(Screen.DASHBOARD)} className="text-sm font-medium text-slate-300 hover:text-accent-cyan transition-colors">Dashboard</button>
                  <button className="text-sm font-medium text-white transition-colors relative after:content-[''] after:absolute after:bottom-[-4px] after:left-0 after:w-full after:h-[2px] after:bg-primary after:rounded-full">Analyzer</button>
                  <button className="text-sm font-medium text-slate-300 hover:text-accent-cyan transition-colors">Resume Builder</button>
                  <button className="text-sm font-medium text-slate-300 hover:text-accent-cyan transition-colors">Learning Paths</button>
               </nav>
               <div className="flex items-center gap-4">
                  <button className="relative p-2 text-slate-400 hover:text-white transition-colors"><span className="material-symbols-outlined">notifications</span><span className="absolute top-2 right-2 size-2 bg-red-500 rounded-full"></span></button>
                  <div className="size-9 rounded-full bg-cover bg-center border border-white/10" style={{ backgroundImage: 'url("https://randomuser.me/api/portraits/men/32.jpg")' }}></div>
               </div>
            </div>
         </header>

         <main className="flex-grow w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-10">
            <div className="flex flex-col items-center text-center gap-4 py-4 animate-fade-up">
               <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-semibold uppercase tracking-wider">
                  <span className="material-symbols-outlined text-[16px]">psychology</span> AI Powered Analysis
               </div>
               <h2 className="text-4xl md:text-5xl font-black tracking-tight text-white drop-shadow-lg">Job Description Analyzer</h2>
               <p className="text-slate-400 text-lg max-w-2xl">Paste a job description below to instantly reveal your match score, identify skill gaps, and generate a tailored action plan.</p>
            </div>

            <div className="grid lg:grid-cols-12 gap-8 animate-fade-up" style={{ animationDelay: '0.1s' }}>
               <div className="lg:col-span-5 flex flex-col gap-6">
                  {/* Resume Upload Section */}
                  <GlassCard className="p-1">
                     <div className="bg-[#151921]/50 rounded-xl p-5 flex flex-col gap-4 border border-white/5">
                        <div className="flex justify-between items-center">
                           <label className="text-sm font-semibold text-slate-300 flex items-center gap-2"><span className="material-symbols-outlined text-primary text-[18px]">upload_file</span> Resume Analysis</label>
                        </div>
                        <div
                           onClick={handleUploadClick}
                           className={`border-2 border-dashed ${analyzing ? 'border-primary animate-pulse' : 'border-slate-700'} rounded-xl p-6 flex flex-col items-center justify-center text-center hover:border-primary/50 hover:bg-white/5 transition-all cursor-pointer group`}
                        >
                           {analyzing ? (
                              <div className="flex flex-col items-center">
                                 <span className="material-symbols-outlined text-primary text-4xl animate-spin mb-2">sync</span>
                                 <p className="text-sm text-primary font-medium">Analyzing Resume...</p>
                              </div>
                           ) : (
                              <>
                                 <div className="size-12 rounded-full bg-slate-800 flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                                    <span className="material-symbols-outlined text-slate-400 group-hover:text-primary">cloud_upload</span>
                                 </div>
                                 <p className="text-sm text-slate-300 font-medium">Click to upload or drag and drop</p>
                                 <p className="text-xs text-slate-500 mt-1">PDF, DOCX up to 10MB</p>
                              </>
                           )}
                           <input
                              ref={fileInputRef}
                              type="file"
                              className="hidden"
                              accept=".pdf,.docx"
                              onChange={handleFileChange}
                              disabled={analyzing}
                           />
                        </div>
                        {error && <p className="text-xs text-red-400 text-center">{error}</p>}
                     </div>
                  </GlassCard>

                  <GlassCard className="p-1">
                     <div className="bg-[#151921]/50 rounded-xl p-5 flex flex-col gap-4 h-full border border-white/5">
                        <div className="flex justify-between items-center">
                           <label className="text-sm font-semibold text-slate-300 flex items-center gap-2"><span className="material-symbols-outlined text-primary text-[18px]">description</span> Job Description</label>
                           <button className="text-xs text-primary hover:text-accent-cyan transition-colors">Clear text</button>
                        </div>
                        <textarea className="w-full h-[200px] bg-black/20 rounded-lg p-4 text-sm leading-relaxed text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-1 focus:ring-primary/50 resize-none border-none font-mono" defaultValue={`Senior Frontend Engineer - React/TypeScript...`} />
                        <button className="group relative w-full h-12 bg-gradient-to-r from-primary to-primary-dark hover:from-primary-dark hover:to-primary rounded-xl flex items-center justify-center gap-3 text-white font-bold text-base shadow-[0_0_15px_rgba(0,206,209,0.5)] transition-all hover:scale-[1.02] active:scale-[0.98]">
                           <span className="material-symbols-outlined group-hover:animate-pulse">bolt</span> Analyze Match
                           <div className="absolute inset-0 rounded-xl bg-white/20 blur opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        </button>
                     </div>
                  </GlassCard>
               </div>

               <div className="lg:col-span-7 flex flex-col gap-6">
                  <div className="grid md:grid-cols-2 gap-6">
                     <GlassCard className="p-6 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity"><span className="material-symbols-outlined text-6xl">data_usage</span></div>
                        <h3 className="text-sm font-medium text-slate-400 mb-4">Readiness Score</h3>
                        <div className="flex items-center gap-6">
                           <div className="relative size-32">
                              <svg className="size-full -rotate-90 transform" viewBox="0 0 100 100">
                                 <circle cx="50" cy="50" fill="transparent" r="40" stroke="rgba(255,255,255,0.1)" strokeWidth="8"></circle>
                                 <circle cx="50" cy="50" fill="transparent" r="40" stroke="#00CED1" strokeDasharray={`${getScore() * 2.51} 251`} strokeLinecap="round" strokeWidth="8" className="drop-shadow-[0_0_10px_rgba(0,206,209,0.6)] transition-all duration-1000"></circle>
                              </svg>
                              <div className="absolute inset-0 flex flex-col items-center justify-center"><span className="text-3xl font-black text-white">{getScore()}%</span></div>
                           </div>
                           <div className="flex flex-col gap-2">
                              <p className="text-white font-semibold text-lg">{getScore() > 70 ? 'Good Match' : 'Gap Identified'}</p>
                              <p className="text-sm text-slate-400 leading-snug">Based on your resume analysis.</p>
                           </div>
                        </div>
                     </GlassCard>

                     <GlassCard className="p-6 flex flex-col justify-between">
                        <div className="flex justify-between items-start mb-2">
                           <h3 className="text-sm font-medium text-slate-400">Bridge Gap Estimate</h3>
                           <span className="bg-primary/20 text-primary text-xs px-2 py-1 rounded border border-primary/20">~3 Weeks</span>
                        </div>
                        <div className="relative pt-6 pb-2">
                           <div className="h-1 w-full bg-slate-700 rounded-full relative">
                              <div className="absolute left-0 top-0 h-full w-1/3 bg-gradient-to-r from-green-500 to-primary rounded-full"></div>
                           </div>
                           <div className="absolute top-4 left-0 -translate-x-1/2 flex flex-col items-center">
                              <div className="size-4 bg-green-500 rounded-full border-2 border-[#151921] shadow-[0_0_10px_rgba(34,197,94,0.6)]"></div>
                              <span className="text-[10px] text-slate-400 mt-1">Now</span>
                           </div>
                           <div className="absolute top-4 left-1/3 -translate-x-1/2 flex flex-col items-center">
                              <div className="size-4 bg-primary rounded-full border-2 border-[#151921] shadow-[0_0_10px_rgba(0,206,209,0.5)] animate-pulse"></div>
                              <span className="text-[10px] text-white font-bold mt-1">Learning</span>
                           </div>
                           <div className="absolute top-4 right-0 translate-x-1/2 flex flex-col items-center">
                              <div className="size-4 bg-slate-700 rounded-full border-2 border-[#151921]"></div>
                              <span className="text-[10px] text-slate-400 mt-1">Ready</span>
                           </div>
                        </div>
                        <p className="text-xs text-slate-500 mt-4 italic">Based on 2hrs/day study plan.</p>
                     </GlassCard>
                  </div>

                  <GlassCard className="p-6">
                     <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-bold text-white flex items-center gap-2"><span className="material-symbols-outlined text-primary">hub</span> Skill Matrix</h3>
                        <div className="flex gap-2 text-xs">
                           <div className="flex items-center gap-1 text-green-400"><span className="material-symbols-outlined text-[14px]">check_circle</span> Match</div>
                           <div className="flex items-center gap-1 text-red-400"><span className="material-symbols-outlined text-[14px]">cancel</span> Missing</div>
                        </div>
                     </div>
                     <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Matched Skills */}
                        <div className="flex flex-col gap-3">
                           <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Matched</div>
                           {getMatchedSkills().map((s: any, i: number) => (
                              <div key={i} className="p-3 rounded-lg bg-green-500/10 border border-green-500/20 flex flex-col gap-1 group cursor-default hover:bg-green-500/20 transition-colors">
                                 <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium text-green-100">{s.name || s}</span>
                                    <span className="material-symbols-outlined text-green-400 text-[18px]">check_circle</span>
                                 </div>
                                 {s.reason && <p className="text-[11px] text-green-200/60 leading-tight">{s.reason}</p>}
                              </div>
                           ))}
                        </div>

                        {/* Missing Skills */}
                        <div className="flex flex-col gap-3">
                           <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Gaps</div>
                           {getMissingSkills().map((s: any, i: number) => (
                              <div key={i} className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 flex flex-col gap-1 group hover:bg-red-500/15 transition-colors">
                                 <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium text-red-100">{s.name || s}</span>
                                    <button className="px-2 py-1 rounded bg-red-500/20 text-[10px] font-bold text-red-400 hover:bg-red-500 hover:text-white transition-colors uppercase tracking-wide">Learn</button>
                                 </div>
                                 {s.desc && <p className="text-[11px] text-red-200/60 leading-tight">{s.desc}</p>}
                              </div>
                           ))}
                        </div>
                     </div>
                  </GlassCard>

                  <div className="grid sm:grid-cols-3 gap-4 pt-2">
                     {[
                        { icon: 'description', label: 'Tailor Resume', borderHover: 'hover:border-primary/50', shadowHover: 'hover:shadow-[0_0_15px_rgba(0,206,209,0.5)]', iconColor: 'text-primary', iconBg: 'bg-primary/10' },
                        { icon: 'edit_document', label: 'Cover Letter', borderHover: 'hover:border-accent-violet/50', shadowHover: 'hover:shadow-[0_0_15px_rgba(238,130,238,0.5)]', iconColor: 'text-accent-violet', iconBg: 'bg-accent-violet/10' },
                        { icon: 'school', label: 'Learning Path', borderHover: 'hover:border-green-500/50', shadowHover: 'hover:shadow-[0_0_15px_rgba(34,197,94,0.5)]', iconColor: 'text-green-400', iconBg: 'bg-green-500/10' }
                     ].map((btn, i) => (
                        <button key={i} className={`h-24 rounded-2xl bg-gradient-to-br from-[#151921] to-slate-900 border border-white/10 p-4 flex flex-col items-center justify-center gap-2 transition-all group ${btn.borderHover} ${btn.shadowHover}`}>
                           <div className={`p-2 rounded-full ${btn.iconBg} ${btn.iconColor} group-hover:bg-opacity-100 group-hover:text-white transition-colors`}>
                              <span className="material-symbols-outlined">{btn.icon}</span>
                           </div>
                           <span className="text-sm font-bold text-slate-200">{btn.label}</span>
                        </button>
                     ))}
                  </div>
               </div>
            </div>
         </main>
      </div>
   );
};

export default Analyzer;