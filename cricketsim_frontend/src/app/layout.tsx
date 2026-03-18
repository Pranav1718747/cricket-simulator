import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Link from 'next/link';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'CricketSim AI',
  description: 'Simulate T20 cricket matches using real player stats.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-slate-950 text-slate-100 min-h-screen flex flex-col`}>
        <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <Link href="/" className="text-xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">
                  🏏 CricketSim AI
                </Link>
                <div className="ml-10 flex items-baseline space-x-4">
                  <Link href="/players" className="text-slate-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors">
                    Explore Players
                  </Link>
                  <Link href="/simulate" className="bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 px-3 py-2 rounded-md text-sm font-medium transition-colors">
                    Simulator
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>
        
        <main className="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
          {children}
        </main>
        
        <footer className="border-t border-slate-800 py-6 mt-auto">
          <div className="max-w-7xl mx-auto px-4 text-center text-sm text-slate-500">
            Powered by Next.js & Django &bull; Probabilistic Match Engine
          </div>
        </footer>
      </body>
    </html>
  );
}
