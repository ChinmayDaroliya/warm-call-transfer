// frontend/src/app/agent/b/page.tsx
'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Phone, User, Clock, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function AgentBPage() {
  // This would be similar to Agent A page but for receiving transfers
  // For demo purposes, we'll show a simplified version

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-4">
        <Link href="/agent" className="flex items-center text-blue-600 hover:text-blue-800">
          <ArrowLeft size={16} className="mr-1" />
          Back to Dashboard
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <User className="mr-2" size={24} />
            Agent B - Transfer Request
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="p-4 bg-orange-50 border border-orange-200 rounded-lg">
            <h4 className="font-semibold text-orange-800 mb-2">Transfer from Agent A</h4>
            <p className="text-orange-700">
              Customer needs advanced technical support that requires your expertise in network configuration.
            </p>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-primary rounded-full flex items-center justify-center">
                  <User size={24} className="text-primary-foreground" />
                </div>
                <div>
                  <h3 className="font-semibold">John Doe</h3>
                  <p className="text-sm text-muted-foreground">+1234567890</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-muted-foreground">Transferring</div>
                <div className="text-xs text-muted-foreground flex items-center">
                  <Clock size={12} className="mr-1" />
                  1:15
                </div>
              </div>
            </div>

            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <h4 className="font-semibold text-green-800 mb-2">Call Summary</h4>
              <div className="text-green-700 text-sm space-y-2">
                <p><strong>Issue:</strong> Network connectivity problems with new device</p>
                <p><strong>Steps taken:</strong> Basic troubleshooting, rebooted device</p>
                <p><strong>Current status:</strong> Still experiencing intermittent connectivity</p>
                <p><strong>Next steps:</strong> Advanced network configuration required</p>
              </div>
            </div>
          </div>

          <div className="flex space-x-4">
            <Button className="flex-1">
              <Phone size={16} className="mr-2" />
              Accept Transfer
            </Button>
            <Button variant="outline" className="flex-1">
              Decline Transfer
            </Button>
          </div>

          <div className="text-sm text-muted-foreground">
            <p>• This is a warm transfer from Agent A</p>
            <p>• Call duration: 4 minutes so far</p>
            <p>• Customer sentiment: Patient but frustrated</p>
            <p>• Priority: Medium</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}