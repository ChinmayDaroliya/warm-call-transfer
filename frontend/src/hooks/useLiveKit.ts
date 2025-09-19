// frontend/src/hooks/useLiveKit.ts
import { useState, useEffect, useCallback } from 'react';
import { Room, Participant, Track, RoomEvent } from 'livekit-client';
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
      // Avoid duplicate connections if already connected
      if (isConnected && room) {
        return () => {
          /* no-op cleanup when already connected */
        };
      }

      const connectedRoom = await liveKitService.connect({
        wsUrl: LIVEKIT_WS_URL,
        token,
        options: {
          adaptiveStream: true,
          dynacast: true,
        },
        connectOptions: {
          autoSubscribe: true,
        },
      });

      setRoom(connectedRoom);
      setIsConnected(true);

      // Set initial states safely (room could disconnect immediately on flaky networks)
      const lp = connectedRoom?.localParticipant as any;
      if (lp) {
        const audioPub = lp.getTrackPublication?.(Track.Source.Microphone);
        const videoPub = lp.getTrackPublication?.(Track.Source.Camera);
        const screenPub = lp.getTrackPublication?.(Track.Source.ScreenShare);

        setIsAudioEnabled(audioPub ? !audioPub.isMuted : false);
        setIsVideoEnabled(videoPub ? !videoPub.isMuted : false);
        setIsScreenSharing(screenPub ? screenPub.isSubscribed : false);
      } else {
        setIsAudioEnabled(false);
        setIsVideoEnabled(false);
        setIsScreenSharing(false);
      }

      // Proactively request mic on first connect to surface the permission prompt
      try {
        if (connectedRoom?.localParticipant) {
          const existingMic = connectedRoom.localParticipant.getTrackPublication(Track.Source.Microphone);
          if (!existingMic) {
            await connectedRoom.localParticipant.setMicrophoneEnabled(true);
            setIsAudioEnabled(true);
          }
          const existingCam = connectedRoom.localParticipant.getTrackPublication(Track.Source.Camera);
          if (!existingCam) {
            await connectedRoom.localParticipant.setCameraEnabled(true);
            setIsVideoEnabled(true);
          }
        }
      } catch (e) {
        // Permission might be blocked; leave controls available so user can try again
        console.warn('Microphone permission/enable failed:', e);
      }

      // Listen for participant changes
      const unsubscribeParticipants = liveKitService.onParticipantsChanged(setParticipants);

      // Listen for disconnects to keep UI state in sync
      const handleDisconnected = () => {
        setIsConnected(false);
        setRoom(null);
        setParticipants([]);
      };
      try {
        if ((connectedRoom as any)?.on) {
          connectedRoom.on(RoomEvent.Disconnected as any, handleDisconnected);
        }
      } catch {}

      return () => {
        unsubscribeParticipants();
        try {
          if ((connectedRoom as any)?.off) {
            connectedRoom.off(RoomEvent.Disconnected as any, handleDisconnected);
          }
        } catch {}
        liveKitService.disconnect();
        setIsConnected(false);
        setRoom(null);
        setParticipants([]);
      };
    } catch (error) {
      console.error('Failed to connect to LiveKit:', error);
      throw error;
    }
  }, [isConnected, room]);

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