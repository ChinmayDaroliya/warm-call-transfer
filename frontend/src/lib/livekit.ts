import {
  Room,
  RoomOptions,
  RoomEvent,
  Participant,
  TrackPublication,
  Track,
} from 'livekit-client';

export const LIVEKIT_WS_URL =
  process.env.NEXT_PUBLIC_LIVEKIT_WS_URL || 'ws://localhost:7880';

export interface LiveKitConfig {
  wsUrl: string;
  token: string;
  options?: RoomOptions;
}

export class LiveKitService {
  private room: Room | null = null;

  async connect(config: LiveKitConfig): Promise<Room> {
    this.room = new Room(config.options);
    try {
      await this.room.connect(config.wsUrl, config.token);
      return this.room;
    } catch (error) {
      console.error('Failed to connect to LiveKit room:', error);
      throw error;
    }
  }

  disconnect() {
    this.room?.disconnect();
    this.room = null;
  }

  getRoom(): Room | null {
    return this.room;
  }

  async toggleAudio() {
    const local = this.room?.localParticipant;
    if (!local) return;

    const micPub = local.getTrackPublications().find(
      (pub) => pub.source === 'microphone'
    );
    if (!micPub) return;

    await local.setMicrophoneEnabled(!micPub.isMuted);
  }

  async toggleVideo() {
    const local = this.room?.localParticipant;
    if (!local) return;

    const camPub = local.getTrackPublications().find(
      (pub) => pub.source === 'camera'
    );
    if (!camPub) return;

    await local.setCameraEnabled(!camPub.isMuted);
  }

  async shareScreen() {
    const local = this.room?.localParticipant;
    if (!local) return;

    await local.setScreenShareEnabled(true);
  }

  async stopScreenShare() {
    const local = this.room?.localParticipant;
    if (!local) return;

    await local.setScreenShareEnabled(false);
  }

  // Returns array of all participants including local
  onParticipantsChanged(callback: (participants: Participant[]) => void) {
    if (!this.room) return () => {};

    const update = () => {
      const participants = [
        this.room!.localParticipant,
        ...Array.from(this.room!.remoteParticipants.values()),
      ];
      callback(participants);
    };

    this.room.on(RoomEvent.ParticipantConnected, update);
    this.room.on(RoomEvent.ParticipantDisconnected, update);

    update(); // initial call

    return () => {
      this.room?.off(RoomEvent.ParticipantConnected, update);
      this.room?.off(RoomEvent.ParticipantDisconnected, update);
    };
  }

  // Track audio levels
  onAudioLevelChanged(
    callback: (participant: Participant, level: number) => void
  ) {
    if (!this.room) return () => {};

    const attach = (participant: Participant, pub: TrackPublication) => {
      const track = pub.track;
      if (!track) return;

      track.on('volumeChanged' as any, (level: number) => {
        callback(participant, level);
        });

    };

    // existing remote participants
    this.room.remoteParticipants.forEach((p) =>
      p.getTrackPublications().forEach((pub) => attach(p, pub))
    );

    // local participant
    this.room.localParticipant.getTrackPublications().forEach((pub) =>
      attach(this.room!.localParticipant, pub)
    );

    // future participants
    const handle = (p: Participant) => {
      p.getTrackPublications().forEach((pub) => attach(p, pub));
    };
    this.room.on(RoomEvent.ParticipantConnected, handle);

    return () => {
      this.room?.off(RoomEvent.ParticipantConnected, handle);
    };
  }
}

export const liveKitService = new LiveKitService();
