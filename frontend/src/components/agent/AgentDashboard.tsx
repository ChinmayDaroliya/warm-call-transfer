// frontend/src/components/agent/AgentDashboard.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAgentStore } from '@/store';
import { User, Phone, Clock, BarChart3 } from 'lucide-react';

export const AgentDashboard: React.FC = () => {
  const { currentAgent, availableAgents } = useAgentStore();

  const stats = [
    {
      title: 'Total Calls Today',
      value: '24',
      icon: Phone,
      change: '+12%',
      trend: 'up',
    },
    {
      title: 'Average Handle Time',
      value: '4m 32s',
      icon: Clock,
      change: '-2%',
      trend: 'down',
    },
    {
      title: 'Transfer Rate',
      value: '8%',
      icon: BarChart3,
      change: '+3%',
      trend: 'up',
    },
    {
      title: 'Available Agents',
      value: availableAgents.length.toString(),
      icon: User,
      change: `${availableAgents.length}/15`,
      trend: 'neutral',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">
                {stat.change} from yesterday
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Agent Information</CardTitle>
          </CardHeader>
          <CardContent>
            {currentAgent ? (
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                    <User size={24} className="text-primary-foreground" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold">{currentAgent.name}</h3>
                    <p className="text-muted-foreground">{currentAgent.email}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Status</label>
                    <p className="capitalize">{currentAgent.status}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Current Room</label>
                    <p>{currentAgent.current_room_id || 'None'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Max Calls</label>
                    <p>{currentAgent.max_concurrent_calls}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Skills</label>
                    <p>{currentAgent.skills.join(', ') || 'None'}</p>
                  </div>
                </div>
              </div>
            ) : (
              <p>No agent information available</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Call with John Doe</p>
                  <p className="text-sm text-muted-foreground">2 minutes ago</p>
                </div>
                <div className="text-green-500">Completed</div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Transfer to Sarah</p>
                  <p className="text-sm text-muted-foreground">15 minutes ago</p>
                </div>
                <div className="text-blue-500">In Progress</div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Call with Jane Smith</p>
                  <p className="text-sm text-muted-foreground">1 hour ago</p>
                </div>
                <div className="text-green-500">Completed</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};