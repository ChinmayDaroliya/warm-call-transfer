// frontend/src/components/agent/CallSummary.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, Clock, User, Phone } from 'lucide-react';

interface CallSummaryProps {
  summary: string;
  duration: number;
  callerName?: string;
  callerPhone?: string;
  createdAt: string;
}

export const CallSummary: React.FC<CallSummaryProps> = ({
  summary,
  duration,
  callerName,
  callerPhone,
  createdAt,
}) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <FileText className="mr-2" size={20} />
          Call Summary
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-2">
            <User size={16} className="text-muted-foreground" />
            <div>
              <div className="text-sm font-medium">Caller</div>
              <div className="text-sm">{callerName || 'Unknown'}</div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Phone size={16} className="text-muted-foreground" />
            <div>
              <div className="text-sm font-medium">Phone</div>
              <div className="text-sm">{callerPhone || 'Not provided'}</div>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Clock size={16} className="text-muted-foreground" />
            <div>
              <div className="text-sm font-medium">Duration</div>
              <div className="text-sm">
                {Math.floor(duration / 60)}m {duration % 60}s
              </div>
            </div>
          </div>
        </div>

        <div>
          <h4 className="text-sm font-medium mb-2">Summary</h4>
          <div className="bg-muted p-4 rounded-lg">
            <p className="text-sm whitespace-pre-wrap">{summary}</p>
          </div>
        </div>

        <div className="text-sm text-muted-foreground">
          Call ended at {new Date(createdAt).toLocaleString()}
        </div>
      </CardContent>
    </Card>
  );
};