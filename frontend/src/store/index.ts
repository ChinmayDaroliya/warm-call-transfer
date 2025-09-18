// frontend/src/store/index.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { Call, Agent, Transfer, CallStatus, AgentStatus, TransferStatus } from '../lib/types';

interface CallState {
  currentCall: Call | null;
  activeCalls: Call[];
  setCurrentCall: (call: Call | null) => void;
  addActiveCall: (call: Call) => void;
  updateCallStatus: (callId: string, status: CallStatus) => void;
  removeActiveCall: (callId: string) => void;
}

interface AgentState {
  currentAgent: Agent | null;
  availableAgents: Agent[];
  setCurrentAgent: (agent: Agent | null) => void;
  setAvailableAgents: (agents: Agent[]) => void;
  updateAgentStatus: (agentId: string, status: AgentStatus) => void;
}

interface TransferState {
  activeTransfers: Transfer[];
  setActiveTransfers: (transfers: Transfer[]) => void;
  addActiveTransfer: (transfer: Transfer) => void;
  updateTransferStatus: (transferId: string, status: TransferStatus) => void;
  removeActiveTransfer: (transferId: string) => void;
}

interface UIState {
  isSidebarOpen: boolean;
  isTransferModalOpen: boolean;
  toggleSidebar: () => void;
  openTransferModal: () => void;
  closeTransferModal: () => void;
}

export const useCallStore = create<CallState>()(
  devtools((set) => ({
    currentCall: null,
    activeCalls: [],
    setCurrentCall: (call) => set({ currentCall: call }),
    addActiveCall: (call) => set((state) => ({ 
      activeCalls: [...state.activeCalls, call] 
    })),
    updateCallStatus: (callId, status) => set((state) => ({
      activeCalls: state.activeCalls.map(call =>
        call.id === callId ? { ...call, status } : call
      ),
      currentCall: state.currentCall?.id === callId 
        ? { ...state.currentCall, status } 
        : state.currentCall
    })),
    removeActiveCall: (callId) => set((state) => ({
      activeCalls: state.activeCalls.filter(call => call.id !== callId)
    })),
  }))
);

export const useAgentStore = create<AgentState>()(
  devtools((set) => ({
    currentAgent: null,
    availableAgents: [],
    setCurrentAgent: (agent) => set({ currentAgent: agent }),
    setAvailableAgents: (agents) => set({ availableAgents: agents }),
    updateAgentStatus: (agentId, status) => set((state) => ({
      availableAgents: state.availableAgents.map(agent =>
        agent.id === agentId ? { ...agent, status } : agent
      ),
      currentAgent: state.currentAgent?.id === agentId
        ? { ...state.currentAgent, status }
        : state.currentAgent
    })),
  }))
);

export const useTransferStore = create<TransferState>()(
  devtools((set) => ({
    activeTransfers: [],
    setActiveTransfers: (transfers) => set({ activeTransfers: transfers }),
    addActiveTransfer: (transfer) => set((state) => ({
      activeTransfers: [...state.activeTransfers, transfer]
    })),
    updateTransferStatus: (transferId, status) => set((state) => ({
      activeTransfers: state.activeTransfers.map(transfer =>
        transfer.id === transferId ? { ...transfer, status } : transfer
      )
    })),
    removeActiveTransfer: (transferId) => set((state) => ({
      activeTransfers: state.activeTransfers.filter(transfer => transfer.id !== transferId)
    })),
  }))
);

export const useUIStore = create<UIState>()(
  devtools((set) => ({
    isSidebarOpen: false,
    isTransferModalOpen: false,
    toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
    openTransferModal: () => set({ isTransferModalOpen: true }),
    closeTransferModal: () => set({ isTransferModalOpen: false }),
  }))
);