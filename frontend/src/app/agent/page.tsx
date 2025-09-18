// frontend/src/app/agent/page.tsx
'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AgentDashboard } from '../../components/agent/AgentDashboard';
import { useAgentStore } from '@/store';
import { agentsApi } from '@/lib/api';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/ui/button';

export default function AgentPage() {
  const { setCurrentAgent, setAvailableAgents } = useAgentStore();
  const [isLoading, setIsLoading] = React.useState(true);
  const router = useRouter();

  useEffect(() => {
    loadAgentData();
  }, []);

  const loadAgentData = async () => {
    try {
      // In a real app, you'd get the current agent from authentication
      // For now, we'll use a mock agent or fetch from API
      const [agentsResponse] = await Promise.all([
        agentsApi.list(),
        // Add other initial data fetches here
      ]);

      setAvailableAgents(agentsResponse.data);
      
      // Set first agent as current for demo purposes
      if (agentsResponse.data.length > 0) {
        setCurrentAgent(agentsResponse.data[0]);
      }
      
    } catch (error) {
      console.error('Failed to load agent data:', error);
      router.push('/');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
        <span className="ml-2">Loading agent dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Agent Dashboard</h1>
        <div className="flex space-x-4">
          <Button variant="outline" onClick={() => router.push('/agent/a')}>
            Agent A View
          </Button>
          <Button variant="outline" onClick={() => router.push('/agent/b')}>
            Agent B View
          </Button>
        </div>
      </div>

      <AgentDashboard />
    </div>
  );
}