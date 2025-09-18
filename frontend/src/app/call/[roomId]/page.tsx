// frontend/src/app/call/[roomId]/page.tsx
'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useCall } from '@/hooks/useCall';
import { CallInterface } from '@/components/call/CallInterface';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function RoomPage() {
  const params = useParams();
  const roomId = params.roomId as string;
  const { joinCall, currentCall, isLoading } = useCall();
  const [joinError, setJoinError] = useState<string | null>(null);

  useEffect(() => {
    if (roomId) {
      handleJoinRoom();
    }
  }, [roomId]);

  const handleJoinRoom = async () => {
    try {
      // For demo purposes, we'll use a generic participant identity
      // In a real app, you'd get this from authentication
      await joinCall({
        room_id: roomId,
        participant_identity: `participant_${Date.now()}`,
        participant_name: 'Participant',
      });
    } catch (error: any) {
      setJoinError(error.response?.data?.detail || 'Failed to join room');
    }
  };

  const handleDisconnect = () => {
    // Handle disconnect logic
    window.location.href = '/';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <LoadingSpinner size="lg" />
        <span className="ml-2">Joining call...</span>
      </div>
    );
  }

  if (joinError) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="w-96">
          <CardContent className="p-6 text-center">
            <h2 className="text-lg font-semibold text-destructive mb-2">Error Joining Call</h2>
            <p className="text-muted-foreground mb-4">{joinError}</p>
            <Button onClick={() => window.location.href = '/'}>
              Return Home
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (currentCall && currentCall.access_token) {
    return (
      <CallInterface
        token={currentCall.access_token}
        roomName={currentCall.room_id}
        onDisconnect={handleDisconnect}
      />
    );
  }

  return (
    <div className="flex items-center justify-center h-screen">
      <LoadingSpinner size="lg" />
      <span className="ml-2">Connecting...</span>
    </div>
  );
}