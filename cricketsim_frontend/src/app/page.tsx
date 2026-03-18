import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">

      <div className="space-y-4">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight">
          Next-Gen <span className="bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">Cricket</span> Simulation
        </h1>
        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto">
          Draft two teams of your favorite real-world players, and simulate an entire T20 match ball-by-ball. Driven by advanced probablilistic models based on career stats.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 pt-8">
        <Link
          href="/simulate"
          className="px-8 py-4 rounded-full bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-bold text-lg hover:shadow-lg hover:shadow-emerald-500/25 transition-all transform hover:-translate-y-1"
        >
          Start Simulation
        </Link>
        <Link
          href="/players"
          className="px-8 py-4 rounded-full bg-slate-800 text-slate-200 font-medium text-lg border border-slate-700 hover:bg-slate-700 transition-all"
        >
          Explore Player Database
        </Link>
      </div>

      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-left border-t border-slate-800 pt-16 w-full">
        <div className="space-y-2">
          <div className="w-12 h-12 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 text-2xl mb-4">
            📊
          </div>
          <h3 className="text-xl font-semibold text-slate-200">Real Statistics</h3>
          <p className="text-slate-400 text-sm">Every ball outcome is calculated using realistic player career stats, averages, and strike rates.</p>
        </div>
        <div className="space-y-2">
          <div className="w-12 h-12 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400 text-2xl mb-4">
            ⚡
          </div>
          <h3 className="text-xl font-semibold text-slate-200">Ball-by-Ball Engine</h3>
          <p className="text-slate-400 text-sm">Our simulation runs step-by-step through a 20-over match, adapting to match pressure and dynamics.</p>
        </div>
        <div className="space-y-2">
          <div className="w-12 h-12 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400 text-2xl mb-4">
            📈
          </div>
          <h3 className="text-xl font-semibold text-slate-200">Live Visuals</h3>
          <p className="text-slate-400 text-sm">Watch the game unfold with interactive worms, run-rate charts, and ball-by-ball commentary lines.</p>
        </div>
      </div>
    </div>
  );
}
