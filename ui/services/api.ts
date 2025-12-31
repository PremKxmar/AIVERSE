import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const auth = {
  signup: (data: any) => api.post('/auth/signup', data),
  signin: (data: any) => api.post('/auth/signin', data),
  getMe: () => api.get('/auth/me'),
  updateProfile: (data: any) => api.put('/auth/profile', data),
};

export const onboarding = {
  uploadResume: (formData: FormData) => api.post('/onboard/resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  analyzeResume: (formData: FormData) => api.post('/profile/analyze-resume', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  analyzeGithub: (username: string) => api.post(`/profile/analyze-github/${username}`),
};

export const jobs = {
  search: (data: any) => api.post('/jobs/search', data),
  analyze: (data: any) => api.post('/jobs/analyze', data),
  match: (profile: any) => api.post('/jobs/match', { profile }),
  discoverRoles: (profile: any) => api.post('/jobs/discover-roles', profile),
  getTrendingSkills: (domain?: string) => api.get('/jobs/trending-skills', { params: { domain } }),
  getPlatforms: () => api.get('/jobs/platforms'),
};

export const roadmap = {
  generate: (data: any) => api.post('/roadmap/generate', data),
  getDailyTasks: () => api.get('/roadmap/daily'),
  getResources: (data: any) => api.post('/roadmap/resources', data),
};

export const actions = {
  tailorResume: (data: any) => api.post('/action/tailor-resume', data),
  generateCoverLetter: (data: any) => api.post('/action/cover-letter', data),
};

export const evolution = {
  mockInterview: (data: any) => api.post('/evolution/mock-interview', data),
  evaluateAnswer: (data: any) => api.post('/evolution/evaluate-answer', data),
  analyzeRejection: (data: any) => api.post('/evolution/analyze-rejection', data),
};

export const wellness = {
  check: (data: any) => api.post('/wellness/check', data),
  getMotivation: (mood?: string) => api.get('/wellness/motivation', { params: { mood } }),
};

export default api;
