// frontend/src/app/layout.tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './global.css'


const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Warm Transfer System',
  description: 'LiveKit-based warm transfer system with AI summarization',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col">
          
          <main className="flex-1 container mx-auto py-6">
            {children}
          </main>
          
        </div>
      </body>
    </html>
  );
}