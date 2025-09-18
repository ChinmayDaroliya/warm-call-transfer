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
import { CallStatus } from '@/lib/types';

export default function AgentAPage() {
  const [isJoining, setIsJoining] = useState(false);
  const [joinError, setJoinError] = useState<string | null>(null);
  const { joinCall, currentCall, updateStatus } = useCall();
  const { isConnected } = useLiveKit();
  const router = useRouter();

  // Mock call data for demo - in real app, you'd get this from the backend
  const mockCall = {
    id: 'call_123',
    room_id: 'room_abc',
    caller_name: 'John Doe',
    caller_phone: '+1234567890',
    status: 'active',
    agent_a_id: 'agent_1',
    created_at: new Date().toISOString(),
  };

  const handleJoinCall = async () => {
    setIsJoining(true);
    setJoinError(null);
    
    try {
      const response = await joinCall({
        room_id: mockCall.room_id,
        participant_identity: `agent_${mockCall.agent_a_id}`,
        participant_name: 'Agent A',
      });
      
      // Update call status to active
      await updateStatus(mockCall.id, CallStatus.ACTIVE);
      
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

  if (isConnected && currentCall) {
    return (
      <div className="h-screen flex flex-col">
        <div className="flex items-center justify-between p-4 bg-border">
          <h1 className="text-xl font-semibold">Active Call - Agent A</h1>
          <div className="flex items-center space-x-4">
            <TransferButton
              callId={currentCall.id}
              fromAgentId={mockCall.agent_a_id!}
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

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                  <User size={24} className="text-primary-foreground" />
                </div>
                <div>
                  <h3 className="font-semibold">{mockCall.caller_name}</h3>
                  <p className="text-sm text-muted-foreground">{mockCall.caller_phone}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-muted-foreground">Waiting</div>
                <div className="text-xs text-muted-foreground flex items-center">
                  <Clock size={12} className="mr-1" />
                  0:45
                </div>
              </div>
            </div>

            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-semibold text-blue-800 mb-2">Call Reason</h4>
              <p className="text-blue-700">Technical support for product setup and configuration</p>
            </div>
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
            <Button variant="outline" className="flex-1">
              Decline
            </Button>
          </div>

          <div className="text-sm text-muted-foreground">
            <p>• This call has been waiting for 45 seconds</p>
            <p>• Customer needs technical assistance</p>
            <p>• Estimated handle time: 5-7 minutes</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}