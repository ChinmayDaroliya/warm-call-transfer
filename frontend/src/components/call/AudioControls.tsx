// frontend/src/components/call/AudioControls.tsx
import React from 'react';
import { Button } from '@/components/ui/button';
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';

interface AudioControlsProps {
  isAudioEnabled: boolean;
  onToggleAudio: () => void;
  volume: number;
  onVolumeChange: (volume: number) => void;
}

export const AudioControls: React.FC<AudioControlsProps> = ({
  isAudioEnabled,
  onToggleAudio,
  volume,
  onVolumeChange,
}) => {
  return (
    <div className="flex items-center space-x-4">
      <Button
        variant={isAudioEnabled ? 'default' : 'destructive'}
        size="icon"
        onClick={onToggleAudio}
      >
        {isAudioEnabled ? <Mic size={20} /> : <MicOff size={20} />}
      </Button>

      <div className="flex items-center space-x-2">
        <Button
          variant="outline"
          size="icon"
          onClick={() => onVolumeChange(volume > 0 ? 0 : 100)}
        >
          {volume > 0 ? <Volume2 size={20} /> : <VolumeX size={20} />}
        </Button>

        <input
          type="range"
          min="0"
          max="100"
          value={volume}
          onChange={(e) => onVolumeChange(Number(e.target.value))}
          className="w-24"
        />
        <span className="text-sm w-8">{volume}%</span>
      </div>
    </div>
  );
};