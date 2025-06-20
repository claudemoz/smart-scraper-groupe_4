import axios from 'axios';

// Configuration de base d'axios
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les réponses
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Services de données
export const dataService = {
  getProjects: (params = {}) => {
    return api.get('/data', { params });
  },
  
  getProject: (id) => {
    return api.get(`/projects/${id}`);
  },
  
  getStatistics: () => {
    return api.get('/statistics');
  },
  
  getMetadata: () => {
    return api.get('/metadata');
  }
};

// Service de scraper
export const scraperService = {
  trigger: () => {
    return api.post('/scrape');
  },
  
  getStatus: () => {
    return api.get('/scrape/status');
  },
  
  resetLimits: () => {
    return api.post('/scrape/reset-limits');
  }
};

// Service d'authentification
export const authService = {
  login: (credentials) => {
    return api.post('/auth/login', credentials);
  }
};

// Service de santé
export const healthService = {
  check: () => {
    return api.get('/health');
  }
};

export default api; 