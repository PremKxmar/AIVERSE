import React, { useState } from 'react';
import { Screen } from './types';
import Landing from './components/screens/Landing';
import OnboardingFlow from './components/screens/OnboardingFlow';
import Dashboard from './components/screens/Dashboard';
import Analyzer from './components/screens/Analyzer';

const App: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<Screen>(Screen.LANDING);

  const navigate = (screen: Screen) => {
    window.scrollTo(0, 0);
    setCurrentScreen(screen);
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case Screen.LANDING:
        return <Landing onStart={() => navigate(Screen.ONBOARDING_1)} />;
      case Screen.ONBOARDING_1:
      case Screen.ONBOARDING_2:
      case Screen.ONBOARDING_3:
      case Screen.ONBOARDING_4:
      case Screen.ONBOARDING_5:
        return <OnboardingFlow currentStep={currentScreen} onNavigate={navigate} />;
      case Screen.DASHBOARD:
        return <Dashboard onNavigate={navigate} />;
      case Screen.ANALYZER:
        return <Analyzer onNavigate={navigate} />;
      default:
        return <Landing onStart={() => navigate(Screen.ONBOARDING_1)} />;
    }
  };

  return (
    <div className="relative min-h-screen bg-background-dark text-white font-sans selection:bg-primary selection:text-white">
      {/* Dynamic Background Effects - Fixed Position */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-full bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-10"></div>
        <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-primary/10 rounded-full blur-[120px]"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-accent-violet/10 rounded-full blur-[120px]"></div>
      </div>

      {/* Main Content - Relative to stack above background */}
      <div className="relative z-10 w-full flex flex-col min-h-screen">
        {renderScreen()}
      </div>
    </div>
  );
};

export default App;