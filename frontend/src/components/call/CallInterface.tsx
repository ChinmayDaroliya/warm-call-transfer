// frontend/src/components/call/CallInterface.tsx
import React, { useEffect, useRef, useState } from 'react';
import { Participant, Track } from 'livekit-client';
import { useLiveKit } from '@/hooks/useLiveKit';
import { useCall } from '@/hooks/useCall';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Mic, MicOff, Video, VideoOff, ScreenShare, PhoneOff, Users, Volume2, VolumeX } from 'lucide-react';

interface CallInterfaceProps {
  token: string;
  roomName: string;
  onDisconnect: () => void;
}

export const CallInterface: React.FC<CallInterfaceProps> = ({
  token,
  roomName,
  onDisconnect,
}) => {
  const {
    room,
    participants,
    isConnected,
    isAudioEnabled,
    isVideoEnabled,
    isScreenSharing,
    connect,
    disconnect,
    toggleAudio,
    toggleVideo,
    shareScreen,
    stopScreenShare,
  } = useLiveKit();

  const { currentCall } = useCall();
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const [volume, setVolume] = useState(100);
  const [isConnecting, setIsConnecting] = useState(false);

  // Main connection effect
  useEffect(() => {
    let isMounted = true;

    const connectToRoom = async () => {
      if (!token || !roomName || isConnecting) return;
      
      setIsConnecting(true);
      try {
        await connect(token, roomName);
        console.log('Successfully connected to room');
      } catch (error) {
        console.error('Failed to connect to room:', error);
      } finally {
        if (isMounted) {
          setIsConnecting(false);
        }
      }
    };

    if (token && roomName) {
      connectToRoom();
    }

    // Cleanup function - only runs on component unmount
    return () => {
      isMounted = false;
      if (!isConnecting) {
        disconnect();
      }
    };
  }, [token, roomName]); // Remove connect/disconnect from dependencies

  // Local video attachment
  useEffect(() => {
    if (room && localVideoRef.current) {
      room.localParticipant.videoTrackPublications.forEach((publication) => {
        if (publication.track) {
          publication.track.attach(localVideoRef.current!);
        }
      });
    }
  }, [room, isVideoEnabled]);

  // Remote video attachment
  useEffect(() => {
    if (room && remoteVideoRef.current && participants.length > 0) {
      const remoteParticipant = participants.find(p => p.identity !== room.localParticipant.identity);
      if (remoteParticipant) {
        remoteParticipant.videoTrackPublications.forEach((publication) => {
          if (publication.track) {
            publication.track.attach(remoteVideoRef.current!);
          }
        });
      }
    }
  }, [room, participants]);

  // Set volume on remote video element
  useEffect(() => {
    if (remoteVideoRef.current) {
      remoteVideoRef.current.volume = volume / 100;
    }
  }, [volume]);

  const handleDisconnect = () => {
    disconnect();
    onDisconnect();
  };

  const handleVolumeChange = (newVolume: number) => {
    setVolume(newVolume);
  };

  return (
    <div className="flex flex-col h-full bg-gray-100 p-4">
      <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Local Video */}
        <Card>
          <CardContent className="p-4 h-full">
            <div className="flex flex-col h-full">
              <h3 className="text-lg font-semibold mb-2">You</h3>
              <div className="flex-1 bg-black rounded-lg overflow-hidden">
                <video
                  ref={localVideoRef}
                  className="w-full h-full object-cover"
                  muted
                  autoPlay
                  playsInline
                />
                {!isVideoEnabled && (
                  <div className="w-full h-full flex items-center justify-center bg-gray-800">
                    <div className="text-white text-2xl">
                      {currentCall?.caller_name?.charAt(0) || 'U'}
                    </div>
                  </div>
                )}
              </div>
              <div className="mt-2 text-sm text-muted-foreground">
                {currentCall?.caller_name || 'You'}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Remote Video */}
        <Card>
          <CardContent className="p-4 h-full">
            <div className="flex flex-col h-full">
              <h3 className="text-lg font-semibold mb-2">Participant</h3>
              <div className="flex-1 bg-black rounded-lg overflow-hidden">
                <video
                  ref={remoteVideoRef}
                  className="w-full h-full object-cover"
                  autoPlay
                  playsInline
                />
                {participants.length === 0 && (
                  <div className="w-full h-full flex items-center justify-center bg-gray-800">
                    <div className="text-white">
                      {isConnecting ? 'Connecting...' : 'Waiting for participant...'}
                    </div>
                  </div>
                )}
              </div>
              <div className="mt-2 text-sm text-muted-foreground">
                {participants.find(p => p.identity !== room?.localParticipant.identity)?.name || 'Unknown'}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Controls */}
      <div className="flex justify-center space-x-4 mb-4">
        <Button
          variant={isAudioEnabled ? 'default' : 'destructive'}
          size="icon"
          onClick={toggleAudio}
          disabled={!isConnected}
        >
          {isAudioEnabled ? <Mic size={20} /> : <MicOff size={20} />}
        </Button>

        <Button
          variant={isVideoEnabled ? 'default' : 'destructive'}
          size="icon"
          onClick={toggleVideo}
          disabled={!isConnected}
        >
          {isVideoEnabled ? <Video size={20} /> : <VideoOff size={20} />}
        </Button>

        <Button
          variant={isScreenSharing ? 'default' : 'outline'}
          size="icon"
          onClick={isScreenSharing ? stopScreenShare : shareScreen}
          disabled={!isConnected}
        >
          <ScreenShare size={20} />
        </Button>

        <Button variant="outline" size="icon" disabled={!isConnected}>
          <Users size={20} />
          <span className="ml-2">{participants.length + 1}</span>
        </Button>

        <Button variant="destructive" size="icon" onClick={handleDisconnect}>
          <PhoneOff size={20} />
        </Button>
      </div>

      {/* Volume Control */}
      <div className="flex items-center justify-center space-x-2 mb-4">
        <Button
          variant="outline"
          size="icon"
          onClick={() => handleVolumeChange(volume > 0 ? 0 : 100)}
          disabled={!isConnected}
        >
          {volume > 0 ? <Volume2 size={16} /> : <VolumeX size={16} />}
        </Button>
        <input
          type="range"
          min="0"
          max="100"
          value={volume}
          onChange={(e) => handleVolumeChange(Number(e.target.value))}
          className="w-24"
          disabled={!isConnected}
        />
        <span className="text-sm w-8">{volume}%</span>
      </div>

      {/* Status */}
      <div className="text-center text-sm text-muted-foreground">
        {isConnecting ? 'Connecting...' : isConnected ? 'Connected' : 'Disconnected'} | Room: {roomName}
      </div>
    </div>
  );
};