// frontend/src/hooks/useCall.ts
import { useState, useEffect, useCallback } from 'react';
import { useCallStore } from '@/store';
import { callsApi } from '@/lib/api';
import { Call, CallStatus } from '@/lib/types';

export const useCall = () => {
  const { currentCall, setCurrentCall, updateCallStatus } = useCallStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createCall = useCallback(async (callData: any) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await callsApi.create(callData);
      const call: Call = response.data;
      setCurrentCall(call);
      return call;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create call');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [setCurrentCall]);

  const joinCall = useCallback(async (joinData: any) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await callsApi.join(joinData);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to join call');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const endCall = useCallback(async (callId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await callsApi.end(callId);
      setCurrentCall(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to end call');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [setCurrentCall]);

  const updateStatus = useCallback(async (callId: string, status: CallStatus, transcript?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await callsApi.updateStatus(callId, { status, transcript });
      updateCallStatus(callId, status);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update call status');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [updateCallStatus]);

  return {
    currentCall,
    isLoading,
    error,
    createCall,
    joinCall,
    endCall,
    updateStatus,
    clearError: () => setError(null),
  };
};