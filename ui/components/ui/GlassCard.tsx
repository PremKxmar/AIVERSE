import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hoverEffect?: boolean;
}

const GlassCard: React.FC<GlassCardProps> = ({ children, className = '', hoverEffect = false }) => {
  return (
    <div 
      className={`
        glass-panel rounded-2xl border border-white/10 
        ${hoverEffect ? 'transition-all duration-300 hover:border-primary/30 hover:shadow-[0_0_30px_rgba(0,206,209,0.15)] group' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
};

export default GlassCard;