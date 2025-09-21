// frontend/src/app/agent/a/page.tsx
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useCall } from '@/hooks/useCall';
import { useLiveKit } from '@/hooks/useLiveKit';
import { CallInterface } from '@/components/call/CallInterface';
import { TransferButton } from '@/components/call/TransferButton';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Phone, User, Clock } from 'lucide-react';
import { Call, CallStatus, Agent } from '@/lib/types';
import { callsApi, agentsApi, roomsApi } from '@/lib/api';
import { useAgentStore, useCallStore } from '@/store';

export default function AgentAPage() {
  const [isJoining, setIsJoining] = useState(false);
  const [joinError, setJoinError] = useState<string | null>(null);
  const { joinCall, currentCall, updateStatus } = useCall();
  const { isConnected } = useLiveKit();
  const router = useRouter();
  // Use a local agent for this page to avoid being overwritten by other pages
  const [pageAgent, setPageAgent] = useState<Agent | null>(null);
  const { setCurrentCall } = useCallStore();

  const [incomingCall, setIncomingCall] = useState<Call | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  // Ensure we have a local page agent set; prefer the named 'Agent A' (find or create)
  useEffect(() => {
    let mounted = true;
    setIncomingCall(null); // reset on mount to avoid showing stale caller
    const ensureAgent = async () => {
      try {
        // If already Agent A, keep
        if (pageAgent && pageAgent.name?.toLowerCase().includes('agent a')) return;

        // Look for existing Agent A by name among all agents
        const allRes = await agentsApi.list();
        const all = allRes.data || [];
        const agentA = all.find((a: any) => (a.name || '').toLowerCase() === 'agent a');
        if (agentA) {
          if (mounted) setPageAgent(agentA as Agent);
          // Normalize: make Agent A available and others offline to guide auto-assignment
          try {
            await agentsApi.updateStatus(agentA.id, { status: 'available' });
            await Promise.all(
              all
                .filter((a: any) => a.id !== agentA.id && (a.name || '').toLowerCase() !== 'agent b')
                .map((a: any) => agentsApi.updateStatus(a.id, { status: 'offline' }))
            );
          } catch (e) { console.warn('Failed to normalize agents (A):', e); }
          return;
        }

        // Create Agent A if not found
        const created = await agentsApi.create({ name: 'Agent A', email: `agent.a+${Date.now()}@example.com`, skills: [] });
        if (mounted) setPageAgent(created.data as Agent);
        // Ensure new Agent A is available
        try { await agentsApi.updateStatus(created.data.id, { status: 'available' }); } catch {}
      } catch (e) {
        console.error('Failed to ensure agent', e);
      }
    };
    ensureAgent();
    return () => { mounted = false; };
  }, [pageAgent]);

  // Load calls regardless of local agent resolution; prefer assigned, else show newest waiting
  useEffect(() => {
    let mounted = true;
    const loadCalls = async () => {
      try {
        // Manage abort for overlapping requests
        if (abortRef.current) {
          abortRef.current.abort();
        }
        const controller = new AbortController();
        abortRef.current = controller;

        // first load vs refresh indicator
        if (isLoading) {
          setIsLoading(true);
        } else {
          setIsRefreshing(true);
        }
        // Fetch both active and waiting calls
        const [activeRes, waitingRes] = await Promise.all([
          callsApi.list({ status: 'active', _t: Date.now() }, { signal: controller.signal }),
          callsApi.list({ status: 'waiting', _t: Date.now() }, { signal: controller.signal }),
        ]);
        const activeCalls: Call[] = activeRes.data || [];
        let waitingCalls: Call[] = waitingRes.data || [];

        // Use the latest local page agent to avoid cross-tab overwrites
        const latestAgent = pageAgent;
        // Debug logs to inspect data coming from API and store
        console.debug('[Agent A] currentAgent:', latestAgent);
        console.debug('[Agent A] active calls:', activeCalls);
        console.debug('[Agent A] waiting calls:', waitingCalls);

        // Prefer calls assigned to this agent
        const assignedActive = latestAgent ? activeCalls.find(c => c.agent_a_id === latestAgent.id) : null;
        const assignedWaiting = latestAgent ? waitingCalls.find(c => c.agent_a_id === latestAgent.id) : null;

        // Freshness filter: only consider waiting calls within last 10 minutes
        const now = Date.now();
        const TEN_MIN = 10 * 60 * 1000;
        waitingCalls = waitingCalls
          .filter(c => {
            const ts = c.created_at ? new Date(c.created_at).getTime() : 0;
            return ts > 0 && now - ts <= TEN_MIN;
          })
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

        // Build candidate list: assigned first, then newest unassigned waiting
        const candidates: Call[] = [];
        if (assignedActive) candidates.push(assignedActive);
        if (assignedWaiting) candidates.push(assignedWaiting);
        const unassignedWaiting = waitingCalls.filter(c => !c.agent_a_id);
        candidates.push(...unassignedWaiting);

        // Verify LiveKit room actually has a caller connected (identity starts with 'caller_')
        let next: Call | null = null;
        let verifiedAny = false;
        for (const c of candidates.slice(0, 5)) {
          try {
            const resp = await roomsApi.getParticipants(c.room_id, { signal: controller.signal });
            const parts: any[] = resp.data?.participants || resp.data || [];
            verifiedAny = true;
            const hasCaller = Array.isArray(parts) && parts.some((p: any) => (p.identity || '').startsWith('caller_'));
            if (hasCaller) {
              next = c;
              break;
            }
          } catch (e) {
            console.warn('[Agent A] participants check failed for room', c.room_id, e);
          }
        }
        // Fallback: if verification failed or none matched, show the first candidate to avoid hiding valid calls
        if (!next && candidates.length > 0) {
          next = candidates[0];
        }

        console.debug('[Agent A] selected incoming call (assigned-first, otherwise unassigned waiting):', next);

        if (mounted) setIncomingCall(next);
      } catch (e: any) {
        if (e?.name === 'CanceledError') return; // axios cancellation
        console.error('Failed to load waiting calls', e);
        if (mounted) setIncomingCall(null);
      } finally {
        if (mounted) {
          setIsLoading(false);
          setIsRefreshing(false);
        }
      }
    };
    loadCalls();
    const onVisibility = () => {
      if (document.visibilityState === 'visible') {
        loadCalls();
      }
    };
    document.addEventListener('visibilitychange', onVisibility);
    // Faster poll when tab is visible, slower when hidden
    let intervalId = setInterval(loadCalls, 2000);
    const onFocus = () => {
      clearInterval(intervalId);
      intervalId = setInterval(loadCalls, 1500);
      loadCalls();
    };
    const onBlur = () => {
      clearInterval(intervalId);
      intervalId = setInterval(loadCalls, 5000);
    };
    window.addEventListener('focus', onFocus);
    window.addEventListener('blur', onBlur);
    return () => {
      mounted = false;
      clearInterval(intervalId);
      document.removeEventListener('visibilitychange', onVisibility);
      window.removeEventListener('focus', onFocus);
      window.removeEventListener('blur', onBlur);
      if (abortRef.current) abortRef.current.abort();
    };
  }, [pageAgent]);

  const handleJoinCall = async () => {
    setIsJoining(true);
    setJoinError(null);
    
    try {
      if (!incomingCall) throw new Error('No incoming call to join');
      const response = await joinCall({
        room_id: incomingCall.room_id,
        participant_identity: `agent_${pageAgent?.id || 'unknown'}`,
        participant_name: pageAgent?.name || 'Agent',
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
              fromAgentId={pageAgent?.id || ''}
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
            {isRefreshing && (
              <span className="ml-3 text-xs text-muted-foreground">Refreshing…</span>
            )}
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
                    <div className="text-sm text-muted-foreground">{incomingCall.status === 'active' ? 'Active' : 'Waiting'}</div>
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