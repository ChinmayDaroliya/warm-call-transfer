// frontend/src/components/call/TransferButton.tsx
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Users, Repeat  } from 'lucide-react';
import { useTransfer } from '../../hooks/useTransfer';
import { useCall } from '@/hooks/useCall';
import { TransferModal } from '@/components/agent/TransferModal';

interface TransferButtonProps {
  callId: string;
  fromAgentId: string;
}

export const TransferButton: React.FC<TransferButtonProps> = ({
  callId,
  fromAgentId,
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { initiateTransfer, isLoading } = useTransfer();
  const { currentCall } = useCall();

  const handleTransfer = async (toAgentId: string, reason: string) => {
    try {
      await initiateTransfer({
        call_id: callId,
        from_agent_id: fromAgentId,
        to_agent_id: toAgentId,
        reason,
      });
      setIsModalOpen(false);
    } catch (error) {
      console.error('Failed to initiate transfer:', error);
    }
  };

  return (
    <>
      <Button
        variant="outline"
        onClick={() => setIsModalOpen(true)}
        disabled={isLoading || currentCall?.status === 'transferring'}
      >
        <Repeat size={16} className="mr-2" />
        Transfer Call
      </Button>

      <TransferModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onTransfer={handleTransfer}
        currentAgentId={fromAgentId}
      />
    </>
  );
};