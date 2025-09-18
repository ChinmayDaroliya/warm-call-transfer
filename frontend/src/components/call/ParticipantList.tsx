// frontend/src/components/call/ParticipantList.tsx
import React from 'react';
import { Participant, TrackPublication } from 'livekit-client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { User, Mic, MicOff, Video, VideoOff } from 'lucide-react';

interface ParticipantListProps {
  participants: Participant[];
  localParticipant: Participant;
}

export const ParticipantList: React.FC<ParticipantListProps> = ({
  participants,
  localParticipant,
}) => {
  const allParticipants = [localParticipant, ...participants];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">
          Participants ({allParticipants.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {allParticipants.map((participant) => {
            // Convert Maps to arrays
            
                const audioEnabled = participant.getTrackPublications().some(
                    (pub) => pub.track && pub.source === 'microphone' && !pub.isMuted
                    );

                    const videoEnabled = participant.getTrackPublications().some(
                    (pub) => pub.track && pub.source === 'camera' && !pub.isMuted
                    );


            return (
              <div
                key={participant.identity}
                className="flex items-center justify-between p-3 bg-muted rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                    <User size={16} className="text-primary-foreground" />
                  </div>
                  <div>
                    <div className="font-medium">
                      {participant.name || participant.identity}
                      {participant.identity === localParticipant.identity && ' (You)'}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {participant.identity}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {audioEnabled ? (
                    <Mic size={16} className="text-green-500" />
                  ) : (
                    <MicOff size={16} className="text-red-500" />
                  )}
                  {videoEnabled ? (
                    <Video size={16} className="text-green-500" />
                  ) : (
                    <VideoOff size={16} className="text-red-500" />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
