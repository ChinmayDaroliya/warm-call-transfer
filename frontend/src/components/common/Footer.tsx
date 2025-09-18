// frontend/src/components/common/Footer.tsx
import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-background border-t border-border px-6 py-4">
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <div>© 2024 Warm Transfer System. Built with LiveKit.</div>
        <div>LiveKit WebRTC Communication</div>
      </div>
    </footer>
  );
};