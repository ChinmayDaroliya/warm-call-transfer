// frontend/src/app/call/page.tsx
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useCall } from '@/hooks/useCall';
import { CallInterface } from '@/components/call/CallInterface';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Phone, User, Mail } from 'lucide-react';

export default function CallPage() {
  const [callerName, setCallerName] = useState('');
  const [callerPhone, setCallerPhone] = useState('');
  const [callReason, setCallReason] = useState('');
  const [isCallActive, setIsCallActive] = useState(false);
  const [noAgentsAvailable, setNoAgentsAvailable] = useState(false);
  const { createCall, currentCall, isLoading, error } = useCall();
  const router = useRouter();

  const handleStartCall = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const call = await createCall({
        caller_name: callerName,
        caller_phone: callerPhone,
        call_reason: callReason,
        assign_agent: true,
      });
      
      if (call && call.access_token) {
        setIsCallActive(true);
      }

      // If no agent was assigned, inform the caller that agents are busy.
      setNoAgentsAvailable(!call?.agent_a_id);

    } catch (error) {
      console.error('Failed to start call:', error);
    }
  };

  const handleCallEnd = () => {
    setIsCallActive(false);
    router.push('/');
  };

  if (isCallActive && currentCall && currentCall.access_token) {
    return (
      <CallInterface
        token={currentCall.access_token}
        roomName={currentCall.room_id}
        onDisconnect={handleCallEnd}
      />
    );
  }

  return (
    <div className="max-w-md mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Phone className="mr-2" size={24} />
            Start a New Call
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleStartCall} className="space-y-4">
            {error && (
              <div className="bg-destructive/10 text-destructive p-3 rounded-md text-sm">
                {error}
              </div>
            )}

            {noAgentsAvailable && (
              <div className="bg-amber-50 text-amber-800 border border-amber-200 p-3 rounded-md text-sm">
                All agents are currently busy. You are in the queue, please wait for the next available agent.
              </div>
            )}

            <div>
              <Label htmlFor="callerName">Your Name</Label>
              <Input
                id="callerName"
                value={callerName}
                onChange={(e) => setCallerName(e.target.value)}
                placeholder="Enter your name"
                required
              />
            </div>

            <div>
              <Label htmlFor="callerPhone">Phone Number</Label>
              <Input
                id="callerPhone"
                type="tel"
                value={callerPhone}
                onChange={(e) => setCallerPhone(e.target.value)}
                placeholder="Enter your phone number"
              />
            </div>

            <div>
              <Label htmlFor="callReason">Reason for Call</Label>
              <Input
                id="callReason"
                value={callReason}
                onChange={(e) => setCallReason(e.target.value)}
                placeholder="Briefly describe why you're calling"
              />
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Connecting...
                </>
              ) : (
                <>
                  <Phone size={16} className="mr-2" />
                  Start Call
                </>
              )}
            </Button>
          </form>

          <div className="mt-6 p-4 bg-muted rounded-lg">
            <h3 className="font-semibold mb-2 flex items-center">
              <User size={16} className="mr-2" />
              What to Expect
            </h3>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• You'll be connected with the next available agent</li>
              <li>• Average wait time: less than 2 minutes</li>
              <li>• Your call may be transferred for specialized assistance</li>
              <li>• All calls are confidential and secure</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}