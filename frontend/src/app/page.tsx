// frontend/src/app/page.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Phone, User, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="space-y-12 px-4 md:px-8 lg:px-16 py-12">
      
      {/* Hero Section */}
      <div className="text-center max-w-3xl mx-auto space-y-4">
        <h1 className="text-5xl font-extrabold tracking-tight text-gray-900 dark:text-gray-100">
          Warm Transfer System
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300">
          Seamlessly transfer calls between agents with AI-powered summaries and live collaboration.
        </p>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
        {/* Agent Card */}
        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl font-semibold">
              <User size={24} className="text-primary" />
              Join as Agent
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600 dark:text-gray-300">
              Access the agent dashboard to handle customer calls, initiate transfers, and collaborate efficiently.
            </p>
            <Button asChild className="w-full py-2">
              <Link href="/agent" className="flex items-center justify-center gap-2">
                Agent Dashboard <ArrowRight size={16} />
              </Link>
            </Button>
          </CardContent>
        </Card>

        {/* Call Card */}
        <Card className="hover:shadow-lg transition-shadow duration-300">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl font-semibold">
              <Phone size={24} className="text-primary" />
              Start a Call
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-gray-600 dark:text-gray-300">
              Initiate a new customer call and get connected to an available agent quickly.
            </p>
            <Button asChild variant="outline" className="w-full py-2">
              <Link href="/call" className="flex items-center justify-center gap-2">
                Start New Call <ArrowRight size={16} />
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* How It Works Section */}
      <div className="max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 text-center mb-8">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              step: '1',
              title: 'Start Call',
              description: 'Customer connects with an available agent for initial assistance.',
            },
            {
              step: '2',
              title: 'Warm Transfer',
              description: 'Agent initiates transfer with AI-generated call summary for seamless handoff.',
            },
            {
              step: '3',
              title: 'Continue Assistance',
              description: 'New agent continues the conversation with full context from previous discussion.',
            },
          ].map(({ step, title, description }) => (
            <div
              key={step}
              className="text-center p-6 bg-gray-50 dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300"
            >
              <div className="w-12 h-12 bg-primary text-primary-foreground rounded-full flex items-center justify-center mx-auto mb-4 font-semibold">
                {step}
              </div>
              <h3 className="font-semibold text-lg mb-2 text-gray-900 dark:text-gray-100">{title}</h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm">{description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
