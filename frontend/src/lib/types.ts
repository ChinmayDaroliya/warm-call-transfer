// frontend/src/lib/types.ts
export interface Call {
  id: string;
  room_id: string;
  caller_name?: string;
  caller_phone?: string;
  call_reason?: string;
  status: CallStatus;
  agent_a_id?: string;
  agent_b_id?: string;
  access_token?: string;
  created_at: string;
}

export interface Agent {
  id: string;
  name: string;
  email: string;
  status: AgentStatus;
  current_room_id?: string;
  max_concurrent_calls: number;
  skills: string[];
  created_at: string;
  updated_at: string;
}

export interface Transfer {
  id: string;
  call_id: string;
  from_agent_id: string;
  to_agent_id: string;
  status: TransferStatus;
  reason?: string;
  summary_shared?: string;
  initiated_at: string;
  completed_at?: string;
  duration_seconds: number;
  transfer_room_id?: string;
}

export interface RoomInfo {
  room_id: string;
  sid: string;
  max_participants: number;
  creation_time: string;
  metadata?: any;
}

export interface Participant {
  identity: string;
  name: string;
  state: string;
  tracks: TrackInfo[];
  metadata?: string;
  joined_at: string;
  is_publisher: boolean;
}

export interface TrackInfo {
  sid: string;
  name: string;
  type: string;
  muted: boolean;
}

export enum CallStatus {
  WAITING = 'waiting',
  ACTIVE = 'active',
  TRANSFERRING = 'transferring',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum AgentStatus {
  AVAILABLE = 'available',
  BUSY = 'busy',
  OFFLINE = 'offline',
}

export enum TransferStatus {
  INITIATED = 'initiated',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum PriorityLevel {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
  URGENT = 'urgent',
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}