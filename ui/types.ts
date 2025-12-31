export enum Screen {
  LANDING = 'LANDING',
  ONBOARDING_1 = 'ONBOARDING_1',
  ONBOARDING_2 = 'ONBOARDING_2',
  ONBOARDING_3 = 'ONBOARDING_3',
  ONBOARDING_4 = 'ONBOARDING_4',
  ONBOARDING_5 = 'ONBOARDING_5',
  DASHBOARD = 'DASHBOARD',
  ANALYZER = 'ANALYZER'
}

export interface UserProfile {
  name: string;
  email: string;
  role: string;
}
