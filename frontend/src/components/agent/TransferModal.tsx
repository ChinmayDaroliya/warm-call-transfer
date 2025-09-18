// frontend/src/components/agent/TransferModal.tsx
import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useTransfer } from '../../hooks/useTransfer';
import { Agent } from '@/lib/types';

interface TransferModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTransfer: (toAgentId: string, reason: string) => void;
  currentAgentId: string;
}

export const TransferModal: React.FC<TransferModalProps> = ({
  isOpen,
  onClose,
  onTransfer,
  currentAgentId,
}) => {
  const [selectedAgent, setSelectedAgent] = useState('');
  const [reason, setReason] = useState('');
  const [availableAgents, setAvailableAgents] = useState<Agent[]>([]);
  const { getAvailableAgents, isLoading } = useTransfer();

  useEffect(() => {
    if (isOpen) {
      loadAvailableAgents();
    }
  }, [isOpen]);

  const loadAvailableAgents = async () => {
    try {
      const agents = await getAvailableAgents();
      // Filter out current agent
      const filteredAgents = agents.filter((agent: Agent) => agent.id !== currentAgentId);
      setAvailableAgents(filteredAgents);
    } catch (error) {
      console.error('Failed to load available agents:', error);
    }
  };

  const handleTransfer = () => {
    if (selectedAgent && reason) {
      onTransfer(selectedAgent, reason);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Transfer Call</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <Label htmlFor="agent">Transfer To</Label>
            <Select value={selectedAgent} onValueChange={setSelectedAgent}>
              <SelectTrigger>
                <SelectValue placeholder="Select an agent" />
              </SelectTrigger>
              <SelectContent>
                {availableAgents.map((agent) => (
                  <SelectItem key={agent.id} value={agent.id}>
                    {agent.name} - {agent.skills.join(', ')}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="reason">Reason for Transfer</Label>
            <Input
              id="reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Brief reason for transferring this call..."
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleTransfer}
            disabled={!selectedAgent || !reason || isLoading}
          >
            {isLoading ? 'Transferring...' : 'Transfer Call'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};