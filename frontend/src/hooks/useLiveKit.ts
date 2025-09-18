// frontend/src/hooks/useLiveKit.ts
import { useState, useEffect, useCallback } from 'react';
import { Room, Participant, Track } from 'livekit-client';
import { liveKitService, LIVEKIT_WS_URL } from '@/lib/livekit';
import { useCallStore } from '@/store';

export const useLiveKit = () => {
  const { currentCall } = useCallStore();
  const [room, setRoom] = useState<Room | null>(null);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isAudioEnabled, setIsAudioEnabled] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);

  const connect = useCallback(async (token: string, roomName: string) => {
    try {
      const connectedRoom = await liveKitService.connect({
        wsUrl: LIVEKIT_WS_URL,
        token,
        options: {
          adaptiveStream: true,
          dynacast: true,
        },
      });

      setRoom(connectedRoom);
      setIsConnected(true);

      // Set initial states
      const audioPub = connectedRoom.localParticipant.getTrackPublication(Track.Source.Microphone);
      const videoPub = connectedRoom.localParticipant.getTrackPublication(Track.Source.Camera);
      const screenPub = connectedRoom.localParticipant.getTrackPublication(Track.Source.ScreenShare);
      
      setIsAudioEnabled(audioPub ? !audioPub.isMuted : false);
      setIsVideoEnabled(videoPub ? !videoPub.isMuted : false);
      setIsScreenSharing(screenPub ? screenPub.isSubscribed : false);

      // Listen for participant changes
      const unsubscribeParticipants = liveKitService.onParticipantsChanged(setParticipants);

      return () => {
        unsubscribeParticipants();
        liveKitService.disconnect();
        setIsConnected(false);
        setRoom(null);
      };
    } catch (error) {
      console.error('Failed to connect to LiveKit:', error);
      throw error;
    }
  }, []);

  const disconnect = useCallback(() => {
    liveKitService.disconnect();
    setIsConnected(false);
    setRoom(null);
    setParticipants([]);
  }, []);

  const toggleAudio = useCallback(async () => {
    if (room) {
      await liveKitService.toggleAudio();
      const audioPub = room.localParticipant.getTrackPublication(Track.Source.Microphone);
      setIsAudioEnabled(audioPub ? !audioPub.isMuted : false);
    }
  }, [room]);

  const toggleVideo = useCallback(async () => {
    if (room) {
      await liveKitService.toggleVideo();
      const videoPub = room.localParticipant.getTrackPublication(Track.Source.Camera);
      setIsVideoEnabled(videoPub ? !videoPub.isMuted : false);
    }
  }, [room]);

  const shareScreen = useCallback(async () => {
    if (room) {
      await liveKitService.shareScreen();
      setIsScreenSharing(true);
    }
  }, [room]);

  const stopScreenShare = useCallback(async () => {
    if (room) {
      await liveKitService.stopScreenShare();
      setIsScreenSharing(false);
    }
  }, [room]);

  useEffect(() => {
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [room]);

  return {
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
  };
};