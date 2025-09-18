// frontend/src/lib/api.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
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
  create: (data: any) => api.post('/api/calls/create', data),
  join: (data: any) => api.post('/api/calls/join', data),
  get: (callId: string) => api.get(`/api/calls/${callId}`),
  list: (params?: any) => api.get('/api/calls', { params }),
  updateStatus: (callId: string, data: any) => api.put(`/api/calls/${callId}/status`, data),
  end: (callId: string) => api.delete(`/api/calls/${callId}`),
};

export const agentsApi = {
  create: (data: any) => api.post('/api/agents', data),
  list: (params?: any) => api.get('/api/agents', { params }),
  get: (agentId: string) => api.get(`/api/agents/${agentId}`),
  update: (agentId: string, data: any) => api.put(`/api/agents/${agentId}`, data),
  updateStatus: (agentId: string, data: any) => api.patch(`/api/agents/${agentId}/status`, data),
  delete: (agentId: string) => api.delete(`/api/agents/${agentId}`),
};

export const transferApi = {
  initiate: (data: any) => api.post('/api/transfer/initiate', data),
  complete: (transferId: string) => api.post(`/api/transfer/${transferId}/complete`),
  cancel: (transferId: string, reason?: string) => 
    api.post(`/api/transfer/${transferId}/cancel`, { reason }),
  getStatus: (transferId: string) => api.get(`/api/transfer/${transferId}/status`),
  getAvailableAgents: () => api.get('/api/transfer/agents/available'),
  getActiveTransfers: () => api.get('/api/transfer/active'),
};

export const roomsApi = {
  getInfo: (roomId: string) => api.get(`/api/rooms/${roomId}/info`),
  getParticipants: (roomId: string) => api.get(`/api/rooms/${roomId}/participants`),
  getStats: (roomId: string) => api.get(`/api/rooms/${roomId}/stats`),
  close: (roomId: string) => api.delete(`/api/rooms/${roomId}`),
  muteParticipant: (roomId: string, participantIdentity: string, trackType?: string) =>
    api.post(`/api/rooms/${roomId}/mute`, { participantIdentity, trackType }),
  removeParticipant: (roomId: string, participantIdentity: string) =>
    api.post(`/api/rooms/${roomId}/remove`, { participantIdentity }),
  sendData: (roomId: string, data: string, participantIdentity?: string) =>
    api.post(`/api/rooms/${roomId}/send-data`, { data, participantIdentity }),
};