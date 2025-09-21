// frontend/src/lib/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // Prevent caching so agents always see the freshest state
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Expires': '0',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const callsApi = {
  create: (data: any) => api.post('/routers/calls/create', data),
  join: (data: any) => api.post('/routers/calls/join', data),
  get: (callId: string, config?: any) => api.get(`/routers/calls/${callId}`, { ...(config || {}) }),
  list: (params?: any, config?: any) => api.get('/routers/calls', { params, ...(config || {}) }),
  updateStatus: (callId: string, data: any) => api.put(`/routers/calls/${callId}/status`, data),
  end: (callId: string) => api.delete(`/routers/calls/${callId}`),
};

export const agentsApi = {
  create: (data: any) => api.post('/routers/agents', data),
  list: (params?: any, config?: any) => api.get('/routers/agents', { params, ...(config || {}) }),
  get: (agentId: string, config?: any) => api.get(`/routers/agents/${agentId}`, { ...(config || {}) }),
  update: (agentId: string, data: any) => api.put(`/routers/agents/${agentId}`, data),
  updateStatus: (agentId: string, data: any) => api.patch(`/routers/agents/${agentId}/status`, data),
  delete: (agentId: string) => api.delete(`/routers/agents/${agentId}`),
};

export const transferApi = {
  initiate: (data: any) => api.post('/routers/transfer/initiate', data),
  complete: (transferId: string) => api.post(`/routers/transfer/${transferId}/complete`),
  cancel: (transferId: string, reason?: string) => 
    api.post(`/routers/transfer/${transferId}/cancel`, { reason }),
  getStatus: (transferId: string) => api.get(`/routers/transfer/${transferId}/status`),
  getAvailableAgents: () => api.get('/routers/transfer/agents/available'),
  getActiveTransfers: () => api.get('/routers/transfer/active'),
};

export const roomsApi = {
  getInfo: (roomId: string, config?: any) => api.get(`/rooms/${roomId}/info`, { ...(config || {}) }),
  getParticipants: (roomId: string, config?: any) => api.get(`/rooms/${roomId}/participants`, { ...(config || {}) }),
  getStats: (roomId: string, config?: any) => api.get(`/rooms/${roomId}/stats`, { ...(config || {}) }),
  close: (roomId: string, config?: any) => api.delete(`/rooms/${roomId}`, { ...(config || {}) }),
  muteParticipant: (roomId: string, participantIdentity: string, trackType?: string) =>
    api.post(`/rooms/${roomId}/mute`, { participantIdentity, trackType }),
  removeParticipant: (roomId: string, participantIdentity: string) =>
    api.post(`/rooms/${roomId}/remove`, { participantIdentity }),
  sendData: (roomId: string, data: string, participantIdentity?: string) =>
    api.post(`/rooms/${roomId}/send-data`, { data, participantIdentity }),
};