// frontend/src/hooks/useTransfer.ts
import { useState, useCallback } from 'react';
import { useTransferStore } from '@/store';
import { transferApi } from '@/lib/api';
import { Transfer, TransferStatus } from '@/lib/types';

export const useTransfer = () => {
  const { addActiveTransfer, updateTransferStatus, removeActiveTransfer } = useTransferStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initiateTransfer = useCallback(async (transferData: any) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await transferApi.initiate(transferData);
      const transfer: Transfer = {
        id: response.data.transfer_id,
        call_id: transferData.call_id,
        from_agent_id: transferData.from_agent_id,
        to_agent_id: transferData.to_agent_id,
        status: TransferStatus.INITIATED,
        reason: transferData.reason,
        initiated_at: new Date().toISOString(),
        duration_seconds: 0,
      };
      
      addActiveTransfer(transfer);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to initiate transfer');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [addActiveTransfer]);

  const completeTransfer = useCallback(async (transferId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await transferApi.complete(transferId);
      updateTransferStatus(transferId, TransferStatus.COMPLETED);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to complete transfer');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [updateTransferStatus]);

  const cancelTransfer = useCallback(async (transferId: string, reason?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await transferApi.cancel(transferId, reason);
      updateTransferStatus(transferId, TransferStatus.FAILED);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to cancel transfer');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [updateTransferStatus]);

  const getAvailableAgents = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await transferApi.getAvailableAgents();
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get available agents');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    initiateTransfer,
    completeTransfer,
    cancelTransfer,
    getAvailableAgents,
    clearError: () => setError(null),
  };
};