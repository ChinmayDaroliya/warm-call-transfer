// frontend/src/app/agent/a/page.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useCall } from '@/hooks/useCall';
import { useLiveKit } from '@/hooks/useLiveKit';
import { CallInterface } from '@/components/call/CallInterface';
import { TransferButton } from '@/components/call/TransferButton';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Phone, User, Clock } from 'lucide-react';
import { Call, CallStatus } from '@/lib/types';
import { callsApi, agentsApi } from '@/lib/api';
import { useAgentStore, useCallStore } from '@/store';

export default function AgentAPage() {
  const [isJoining, setIsJoining] = useState(false);
  const [joinError, setJoinError] = useState<string | null>(null);
  const { joinCall, currentCall, updateStatus } = useCall();
  const { isConnected } = useLiveKit();
  const router = useRouter();
  const { currentAgent } = useAgentStore();
  const { setCurrentCall } = useCallStore();
  const { setCurrentAgent } = useAgentStore.getState();

  const [incomingCall, setIncomingCall] = useState<Call | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Ensure we have a current agent set; if none, pick first available or create one
  useEffect(() => {
    let mounted = true;
    const ensureAgent = async () => {
      try {
        if (currentAgent) return;
        const res = await agentsApi.list({ status: 'available' });
        const agents = res.data || [];
        if (agents.length > 0) {
          if (mounted) useAgentStore.getState().setCurrentAgent(agents[0]);
          return;
        }
        // create a default agent if none exist
        const created = await agentsApi.create({ name: 'Agent A', email: `agent.a+${Date.now()}@example.com`, skills: [] });
        if (mounted) useAgentStore.getState().setCurrentAgent(created.data);
      } catch (e) {
        console.error('Failed to ensure agent', e);
      }
    };
    ensureAgent();
    return () => { mounted = false; };
  }, [currentAgent]);

  // Load active call assigned to Agent A (only show when call has started)
  useEffect(() => {
    let mounted = true;
    const loadCalls = async () => {
      try {
        setIsLoading(true);
        const res = await callsApi.list({ status: 'active' });
        const calls: Call[] = res.data || [];
        // Only surface calls assigned to this agent. If none are assigned, treat as no incoming call.
        const assigned = currentAgent ? calls.find(c => c.agent_a_id === currentAgent.id) : null;
        if (mounted) setIncomingCall(assigned || null);
      } catch (e) {
        console.error('Failed to load waiting calls', e);
        if (mounted) setIncomingCall(null);
      } finally {
        if (mounted) setIsLoading(false);
      }
    };
    loadCalls();
    const id = setInterval(loadCalls, 4000); // simple poll
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, [currentAgent]);

  const handleJoinCall = async () => {
    setIsJoining(true);
    setJoinError(null);
    
    try {
      if (!incomingCall) throw new Error('No incoming call to join');
      const response = await joinCall({
        room_id: incomingCall.room_id,
        participant_identity: `agent_${currentAgent?.id || 'unknown'}`,
        participant_name: currentAgent?.name || 'Agent',
      });
      
      // Merge token into currentCall and set in store so CallInterface can use it
      setCurrentCall({ ...incomingCall, access_token: response.access_token } as Call);
      // Update call status to active
      await updateStatus(incomingCall.id, CallStatus.ACTIVE);
      
    } catch (error: any) {
      setJoinError(error.response?.data?.detail || 'Failed to join call');
    } finally {
      setIsJoining(false);
    }
  };

  const handleCallEnd = async () => {
    if (currentCall) {
      await updateStatus(currentCall.id, CallStatus.COMPLETED);
    }
    router.push('/agent');
  };

  if (currentCall && currentCall.access_token) {
    return (
      <div className="h-screen flex flex-col">
        <div className="flex items-center justify-between p-4 bg-border">
          <h1 className="text-xl font-semibold">Active Call - Agent A</h1>
          <div className="flex items-center space-x-4">
            <TransferButton
              callId={currentCall.id}
              fromAgentId={currentAgent?.id || ''}
            />
            <Button variant="destructive" onClick={handleCallEnd}>
              End Call
            </Button>
          </div>
        </div>
        <CallInterface
          token={currentCall.access_token!}
          roomName={currentCall.room_id}
          onDisconnect={handleCallEnd}
        />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <User className="mr-2" size={24} />
            Agent A - Incoming Call
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {joinError && (
            <div className="bg-destructive/10 text-destructive p-3 rounded-md">
              {joinError}
            </div>
          )}

          {isLoading ? (
            <div className="p-6 text-muted-foreground">Loading...</div>
          ) : incomingCall ? (
            <>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                      <User size={24} className="text-primary-foreground" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{incomingCall.caller_name || 'Unknown Caller'}</h3>
                      {incomingCall.caller_phone && (
                        <p className="text-sm text-muted-foreground">{incomingCall.caller_phone}</p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-muted-foreground">Active</div>
                    <div className="text-xs text-muted-foreground flex items-center">
                      <Clock size={12} className="mr-1" />
                      {incomingCall.created_at ? new Date(incomingCall.created_at).toLocaleTimeString() : ''}
                    </div>
                  </div>
                </div>

                {incomingCall.call_reason && (
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="font-semibold text-blue-800 mb-2">Call Reason</h4>
                    <p className="text-blue-700">{incomingCall.call_reason}</p>
                  </div>
                )}
              </div>

              <div className="flex space-x-4">
                <Button
                  onClick={handleJoinCall}
                  disabled={isJoining}
                  className="flex-1"
                >
                  {isJoining ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Joining...
                    </>
                  ) : (
                    <>
                      <Phone size={16} className="mr-2" />
                      Accept Call
                    </>
                  )}
                </Button>
                {/* Optional: Add decline action if supported by backend */}
              </div>
            </>
          ) : (
            <div className="p-10 text-center text-muted-foreground">
              <div className="mx-auto mb-3 w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                <Phone size={18} />
              </div>
              <div className="font-medium">No incoming calls</div>
              <div className="text-sm">You will see calls here when they are assigned to you.</div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}