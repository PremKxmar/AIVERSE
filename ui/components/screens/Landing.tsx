import React from 'react';
import Button from '../ui/Button';
import GlassCard from '../ui/GlassCard';

interface LandingProps {
  onStart: () => void;
}

const Landing: React.FC<LandingProps> = ({ onStart }) => {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="fixed top-0 z-50 w-full border-b border-white/10 bg-[#0B0C10]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative flex items-center justify-center size-8 rounded-lg bg-primary/20 text-primary border border-primary/30">
                <span className="material-symbols-outlined text-[20px]">rocket_launch</span>
                <div className="absolute -top-1 -right-1 w-2 h-2 bg-primary rounded-full animate-pulse shadow-[0_0_10px_rgba(0,206,209,1)]"></div>
              </div>
              <span className="font-bold text-lg tracking-tight text-white">Career<span className="text-primary">Companion</span>.ai</span>
            </div>
            <nav className="hidden md:flex gap-8">
              {['Features', 'How it Works', 'Pricing'].map((item) => (
                <a key={item} href="#" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">{item}</a>
              ))}
            </nav>
            <div className="flex items-center gap-4">
              <button className="hidden md:flex text-sm font-medium text-gray-300 hover:text-white transition-colors">Sign In</button>
              <Button size="sm" onClick={onStart}>Get Started</Button>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-grow pt-24">
        {/* Hero Section */}
        <section className="relative pb-16 md:pb-24 overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div className="flex flex-col items-start gap-6 max-w-2xl z-10 animate-fade-up">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
                  </span>
                  <span className="text-xs font-medium text-primary/80 tracking-wide uppercase">AI-Powered Career Growth</span>
                </div>
                <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black tracking-tight leading-[1.1]">
                  From Confusion <br />
                  to <span className="text-gradient">Clarity</span>
                </h1>
                <p className="text-lg text-gray-400 leading-relaxed max-w-lg">
                  Stop guessing. Let <span className="text-white font-semibold">7 specialized AI agents</span> analyze your skills, scan job descriptions for red flags, and build your personalized roadmap to hired.
                </p>
                <div className="flex flex-wrap gap-4 mt-4 w-full sm:w-auto">
                  <Button size="lg" icon="arrow_forward" onClick={onStart}>Start Your Journey</Button>
                  <Button size="lg" variant="secondary" icon="play_circle" iconPosition="left">Watch Demo</Button>
                </div>
                <div className="flex items-center gap-4 mt-4 text-sm text-gray-500">
                  <div className="flex -space-x-2">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="h-8 w-8 rounded-full ring-2 ring-[#0B0C10] bg-gray-700 bg-cover bg-center" style={{backgroundImage: `url(https://randomuser.me/api/portraits/thumb/men/${i*10}.jpg)`}}></div>
                    ))}
                  </div>
                  <p>Joined by <span className="text-white font-bold">10,000+</span> developers</p>
                </div>
              </div>

              {/* 3D Visual */}
              <div className="relative h-[500px] lg:h-[600px] flex items-center justify-center animate-fade-up" style={{animationDelay: '0.2s'}}>
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-primary/30 rounded-full blur-[80px] animate-pulse"></div>
                <div className="animate-float relative w-full max-w-md">
                   <div className="relative z-20 rounded-2xl overflow-hidden shadow-2xl shadow-primary/20 border border-white/10 bg-[#151921]">
                     <img 
                       src="https://lh3.googleusercontent.com/aida-public/AB6AXuB4kd-GXSkOTsdEM2RfY66fcLDHuDoB6Y6AUtCu1eaOahWEUbXaVrV-9bSm6drnzcSNeEph2zOVnLUa-SKxzPGLRkeHlPpiYc0gayJXL8iwbOQHNLd6-uLjN34k3HjJcen7_8gxcYfTPwQG2peBdX03o3fJ1Wtim-2eb0btkfKYMcEqlDZZi43TXWvNRwNCPE3p2Cq78VrH2O7J0Bu-94QFlcgYldOu81YFp1gcrMYUyJlEQeOUUkISXL-98kaCSGW-bP5aa3fnVKY" 
                       alt="AI Robot Head"
                       className="w-full h-auto object-cover opacity-90"
                     />
                     <div className="absolute bottom-4 left-4 right-4 p-4 glass-panel rounded-xl flex items-center gap-3">
                       <div className="flex items-center justify-center size-10 rounded-full bg-green-500/20 text-green-400">
                         <span className="material-symbols-outlined text-[20px]">check_circle</span>
                       </div>
                       <div>
                         <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Analysis Complete</p>
                         <p className="text-sm text-white font-medium">Resume optimized for ATS</p>
                       </div>
                     </div>
                     <div className="absolute top-6 right-6 p-2 glass-panel rounded-lg flex items-center gap-2 animate-bounce" style={{animationDuration: '3s'}}>
                       <div className="w-2 h-2 rounded-full bg-primary"></div>
                       <span className="text-xs font-bold text-white">AI Active</span>
                     </div>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="py-10 border-y border-white/5 bg-white/[0.02]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center divide-y md:divide-y-0 md:divide-x divide-white/10">
              {[
                { label: 'Platforms Indexed', value: '40+' },
                { label: 'AI Agents Active', value: '7' },
                { label: 'Real-time Analysis', value: '100%' },
              ].map((stat) => (
                <div key={stat.label} className="flex flex-col items-center gap-1 p-4">
                  <span className="text-4xl font-black text-white tracking-tight">{stat.value}</span>
                  <span className="text-primary font-medium text-sm uppercase tracking-wider">{stat.label}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Feature Grid */}
        <section className="relative py-24">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-3xl mx-auto mb-20">
              <h2 className="text-3xl md:text-5xl font-black mb-6 tracking-tight">
                Glassmorphic <span className="text-primary">Intelligence</span>
              </h2>
              <p className="text-gray-400 text-lg">
                Advanced tools designed to navigate the modern job market with precision. 
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { icon: 'radar', title: 'JD Hard-Truth Scanner', desc: 'Detects hidden red flags in job posts using NLP.', color: 'text-primary' },
                { icon: 'map', title: 'AI Learning Roadmap', desc: 'Personalized curriculum generated based on skill gaps.', color: 'text-[#EE82EE]' },
                { icon: 'mic', title: 'Mock Interviewer', desc: 'Real-time voice feedback to ace your interviews.', color: 'text-[#00FFFF]' },
                { icon: 'monitor_heart', title: 'Burnout Detection', desc: 'Mental health monitoring for job seeker well-being.', color: 'text-red-400' },
              ].map((feature, idx) => (
                <GlassCard key={idx} hoverEffect className="p-6 relative overflow-hidden group">
                  <div className={`size-12 rounded-xl bg-white/5 flex items-center justify-center ${feature.color} mb-6`}>
                    <span className="material-symbols-outlined text-[28px]">{feature.icon}</span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
                  <p className="text-sm text-gray-400 leading-relaxed">{feature.desc}</p>
                </GlassCard>
              ))}
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/10 bg-[#0B0C10] pt-12 pb-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-600">
           © 2024 AI Career Companion. All rights reserved.
        </div>
      </footer>
    </div>
  );
};

export default Landing;