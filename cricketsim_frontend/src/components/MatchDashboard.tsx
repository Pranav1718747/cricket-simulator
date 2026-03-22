import { useState, useEffect, useRef } from 'react';

interface MatchDashboardProps {
    matchData: any;
}

export default function MatchDashboard({ matchData }: MatchDashboardProps) {
    const [isPlaying, setIsPlaying] = useState(true);
    const [playbackSpeed, setPlaybackSpeed] = useState(1000); // ms per ball
    const [currentBallIndex, setCurrentBallIndex] = useState(0);

    const logRef = useRef<HTMLDivElement>(null);

    if (!matchData) return null;

    const { team_a, team_b, scorecard, simulation_log, winner, pitch_type, dew_factor, match_meta } = matchData;

    const sc1 = scorecard.innings_1 || scorecard[team_a.name];
    const sc2 = scorecard.innings_2 || scorecard[team_b.name];

    const firstBattingTeamName = sc1?.team_name || match_meta?.batting_first_team || team_a.name;
    const secondBattingTeamName = sc2?.team_name || (firstBattingTeamName === team_a.name ? (team_b?.name || "Team B") : (team_a?.name || "Team A"));

    const innings1Log = (simulation_log.innings_1 || []).filter((b: any) => b.outcome !== 'END');
    const innings2Log = (simulation_log.innings_2 || []).filter((b: any) => b.outcome !== 'END');
    const totalBalls = innings1Log.length + innings2Log.length;

    // --- PLAYBACK LOGIC ---
    useEffect(() => {
        let interval: NodeJS.Timeout;
        if (isPlaying && currentBallIndex < totalBalls) {
            interval = setInterval(() => {
                setCurrentBallIndex(prev => prev + 1);
            }, playbackSpeed);
        }
        return () => clearInterval(interval);
    }, [isPlaying, currentBallIndex, totalBalls, playbackSpeed]);

    // Auto scroll commentary
    useEffect(() => {
        if (logRef.current) {
            logRef.current.scrollTop = logRef.current.scrollHeight;
        }
    }, [currentBallIndex]);

    const isFinished = currentBallIndex >= totalBalls;

    // --- DERIVE STATE UP TO CURRENT BALL ---
    const currentI1Balls = innings1Log.slice(0, Math.min(currentBallIndex, innings1Log.length));
    const isI2 = currentBallIndex > innings1Log.length;
    const currentI2Balls = isI2 ? innings2Log.slice(0, currentBallIndex - innings1Log.length) : [];



    // Reducer to calculate live scorecard from played balls
    const deriveScorecard = (teamName: string, log: any[], origScorecard: any) => {
        // Initialize blank scorecard using players from origScorecard
        const sc: any = {
            total_runs: 0,
            wickets: 0,
            overs: 0.0,
            batsmen: {},
            bowlers: {},
            striker: null,
            nonStriker: null,
            currentBowler: null,
            lastSixBalls: []
        };

        // Setup empty stats
        for (const player in origScorecard.batsmen) {
            sc.batsmen[player] = { runs: 0, balls: 0, fours: 0, sixes: 0, out: false };
        }
        for (const player in origScorecard.bowlers) {
            sc.bowlers[player] = { overs: 0.0, runs: 0, wickets: 0 };
        }

        if (log.length === 0) return sc;

        let lastOver = "0", lastBall = "0";

        let striker: string | null = null;
        let nonStriker: string | null = null;

        log.filter((ball: any) => ball.outcome !== 'END' && ball.batsman).forEach((ball: any, idx: number) => {
            const [ov, b] = ball.over.split('.');
            const isEndOfOver = b === '6';

            if (lastOver !== ov) {
                // Swap strikers at end of over
                const temp = striker;
                striker = nonStriker;
                nonStriker = temp;
                lastOver = ov;
            }
            lastBall = b;

            const batsman = ball.batsman;
            const bowler = ball.bowler;
            const outcome = ball.outcome;

            sc.currentBowler = bowler;

            // Initialize position if not set
            if (!striker) striker = batsman;
            else if (striker !== batsman && !nonStriker) nonStriker = batsman;

            // Ensure striker is correct based on the ball record
            if (batsman === nonStriker) {
                const temp = striker;
                striker = nonStriker;
                nonStriker = temp;
            }

            // DEFENSIVE CHECK: Ensure player data exists to avoid "Cannot read properties of undefined"
            if (!sc.batsmen[batsman]) {
                sc.batsmen[batsman] = { runs: 0, balls: 0, fours: 0, sixes: 0, out: false };
            }
            if (!sc.bowlers[bowler]) {
                sc.bowlers[bowler] = { overs: 0.0, runs: 0, wickets: 0 };
            }

            sc.batsmen[batsman].balls += 1;

            if (outcome === 'W') {
                sc.wickets += 1;
                sc.batsmen[batsman].out = true;
                sc.bowlers[bowler].wickets += 1;
                // New batter logic
                striker = null;
            } else if (typeof outcome === 'number') {
                sc.total_runs += outcome;
                sc.batsmen[batsman].runs += outcome;
                sc.bowlers[bowler].runs += outcome;

                if (outcome === 4) sc.batsmen[batsman].fours += 1;
                if (outcome === 6) sc.batsmen[batsman].sixes += 1;

                if (outcome % 2 !== 0) {
                    const temp = striker;
                    striker = nonStriker;
                    nonStriker = temp;
                }
            }

            // Track last 6 balls for the over history
            if (lastOver === ov) {
                if (b === '1') sc.lastSixBalls = [];
                sc.lastSixBalls.push(outcome);
            }
        });

        sc.striker = striker;
        sc.nonStriker = nonStriker;

        const completedOvers = parseInt(lastOver);
        const ballsInCurrent = parseInt(lastBall);
        sc.overs = completedOvers + (ballsInCurrent / 6.0);

        // Recalculate bowler overs live precisely
        const bowlerBalls: Record<string, number> = {};
        log.filter((ball: any) => ball.outcome !== 'END' && ball.bowler).forEach((ball: any) => {
            bowlerBalls[ball.bowler] = (bowlerBalls[ball.bowler] || 0) + 1;
        });
        for (const bowler in bowlerBalls) {
            const b = bowlerBalls[bowler];
            sc.bowlers[bowler].overs = Math.floor(b / 6) + ((b % 6) / 6.0);
        }

        return sc;
    };

    const liveSc1 = deriveScorecard(firstBattingTeamName, currentI1Balls, sc1);
    const liveSc2 = deriveScorecard(secondBattingTeamName, currentI2Balls, sc2);


    const renderScorecard = (team: string, sc: any, isActive: boolean) => (
        <div className={`bg-slate-900 rounded-2xl p-6 border transition-all ${isActive ? 'border-emerald-500/50 shadow-[0_0_15px_-3px_rgba(52,211,153,0.2)]' : 'border-slate-800 opacity-60'}`}>
            <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-slate-100">{team} Innings</h3>
                <div className={`text-2xl font-black bg-slate-950 px-4 py-2 rounded-lg ${isActive ? 'text-emerald-400' : 'text-slate-500'}`}>
                    {sc.total_runs}/{sc.wickets} <span className="text-sm font-medium text-slate-500 ml-2">({(Math.floor(sc.overs) + (sc.overs % 1) * 0.6).toFixed(1)} ov)</span>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="text-xs text-slate-500 uppercase bg-slate-950/50">
                        <tr>
                            <th className="px-4 py-3 rounded-tl-lg">Batsman</th>
                            <th className="px-4 py-3">R</th>
                            <th className="px-4 py-3">B</th>
                            <th className="px-4 py-3">4s</th>
                            <th className="px-4 py-3">6s</th>
                            <th className="px-4 py-3 rounded-tr-lg">SR</th>
                        </tr>
                    </thead>
                    <tbody>
                        {Object.entries(sc.batsmen).map(([name, stats]: [string, any], i) => (
                            stats.balls > 0 && (
                                <tr key={name} className="border-b border-slate-800/50 hover:bg-slate-800/20">
                                    <td className={`px-4 py-3 font-medium ${stats.out ? 'text-slate-400' : 'text-slate-100'}`}>
                                        {name} {stats.out ? <span className="text-red-400/80 text-xs ml-2">(out)</span> : <span className="text-emerald-400/80 text-xs ml-2">*</span>}
                                    </td>
                                    <td className="px-4 py-3 font-bold">{stats.runs}</td>
                                    <td className="px-4 py-3 text-slate-400">{stats.balls}</td>
                                    <td className="px-4 py-3 text-slate-400">{stats.fours}</td>
                                    <td className="px-4 py-3 text-slate-400">{stats.sixes}</td>
                                    <td className="px-4 py-3 text-slate-400">
                                        {((stats.runs / stats.balls) * 100).toFixed(1)}
                                    </td>
                                </tr>
                            )
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="overflow-x-auto mt-6">
                <table className="w-full text-sm text-left">
                    <thead className="text-xs text-slate-500 uppercase bg-slate-950/50">
                        <tr>
                            <th className="px-4 py-3 rounded-tl-lg">Bowler</th>
                            <th className="px-4 py-3">O</th>
                            <th className="px-4 py-3">R</th>
                            <th className="px-4 py-3">W</th>
                            <th className="px-4 py-3 rounded-tr-lg">Econ</th>
                        </tr>
                    </thead>
                    <tbody>
                        {Object.entries(sc.bowlers).map(([name, stats]: [string, any]) => {
                            const decimalOvers = stats.overs;
                            const oversStr = (Math.floor(decimalOvers) + (decimalOvers % 1) * 0.6).toFixed(1);

                            return stats.overs > 0 && (
                                <tr key={name} className="border-b border-slate-800/50 hover:bg-slate-800/20">
                                    <td className="px-4 py-3 font-medium text-slate-200">{name}</td>
                                    <td className="px-4 py-3 text-slate-400">{oversStr}</td>
                                    <td className="px-4 py-3 text-slate-400">{stats.runs}</td>
                                    <td className="px-4 py-3 font-bold text-emerald-400">{stats.wickets}</td>
                                    <td className="px-4 py-3 text-slate-400">
                                        {(stats.runs / decimalOvers).toFixed(1)}
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );

    const activeLog = isI2 ? currentI2Balls : currentI1Balls;

    return (
        <div className="space-y-8 animate-in slide-in-from-bottom-8 duration-700">

            {/* CONTROLS & MATCH INFO */}
            <div className="bg-slate-900 rounded-2xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between border border-slate-800 sticky top-20 z-40 shadow-xl gap-4">

                <div className="flex items-center gap-4">
                    <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        className={`w-12 h-12 rounded-full flex items-center justify-center text-xl transition-all flex-shrink-0 ${isPlaying ? 'bg-amber-500/20 text-amber-500 hover:bg-amber-500/30' : 'bg-emerald-500/20 text-emerald-500 hover:bg-emerald-500/30'}`}
                    >
                        {isPlaying ? '⏸' : '▶'}
                    </button>
                    <div>
                        <div className="text-xs text-slate-400 uppercase tracking-wider font-bold mb-1">Live Status</div>
                        <div className="text-sm font-medium text-slate-200">
                            {isFinished ? 'Match Finished' : isI2 ? '2nd Innings in progress' : '1st Innings in progress'}
                        </div>
                    </div>
                </div>

                <div className="flex bg-slate-950 rounded-xl p-2 border border-slate-800 gap-4 text-xs font-bold uppercase tracking-wider text-slate-400">
                    <div className="flex flex-col items-center px-4 border-r border-slate-800">
                        <span className="text-[10px] text-slate-500 mb-1">Pitch</span>
                        <span className="text-emerald-400">{pitch_type || 'Balanced'}</span>
                    </div>
                    <div className="flex flex-col items-center px-4">
                        <span className="text-[10px] text-slate-500 mb-1">Weather</span>
                        <span className="text-cyan-400">{dew_factor ? 'Heavy Dew' : 'Dry Outfield'}</span>
                    </div>
                </div>

                <div className="flex gap-2">
                    <button onClick={() => setPlaybackSpeed(2500)} className={`px-3 py-1.5 rounded text-xs font-bold ${playbackSpeed === 2500 ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' : 'bg-slate-800 text-slate-400'}`}>1x</button>
                    <button onClick={() => setPlaybackSpeed(1000)} className={`px-3 py-1.5 rounded text-xs font-bold ${playbackSpeed === 1000 ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' : 'bg-slate-800 text-slate-400'}`}>2x</button>
                    <button onClick={() => setPlaybackSpeed(100)} className={`px-3 py-1.5 rounded text-xs font-bold ${playbackSpeed === 100 ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' : 'bg-slate-800 text-slate-400'}`}>10x</button>
                    <button onClick={() => setCurrentBallIndex(totalBalls)} className={`px-3 py-1.5 rounded text-xs font-bold bg-slate-800 hover:bg-slate-700 text-slate-400`}>Skip &gt;|</button>
                </div>
            </div>

            {isFinished ? (
                <div className="bg-gradient-to-r from-emerald-900/40 to-cyan-900/40 border border-emerald-500/20 rounded-3xl p-8 text-center backdrop-blur-sm animate-in zoom-in duration-500">
                    <h2 className="text-sm font-bold tracking-widest text-emerald-400 mb-2 uppercase">Match Result</h2>
                    <div className="text-3xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 mb-2 drop-shadow-sm">
                        {winner}
                    </div>
                </div>
            ) : (
                <div className="flex gap-4 items-center justify-center p-4">
                    <div className="text-sm font-bold text-slate-500 tracking-widest uppercase animate-pulse">Live Simulation Running</div>
                    <div className="flex gap-1">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-[bounce_1s_infinite] delay-75"></div>
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-[bounce_1s_infinite] delay-150"></div>
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-[bounce_1s_infinite] delay-300"></div>
                    </div>
                </div>
            )}

            {/* ── IPL VERSUS CARD (Striker vs Bowler) ── */}
            {!isFinished && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-900/50 rounded-3xl p-1 border border-slate-800 overflow-hidden">
                    {/* Striker */}
                    <div className="bg-slate-900 p-6 rounded-2xl flex flex-col items-center justify-center text-center">
                        <div className="text-[10px] text-emerald-400 font-black uppercase tracking-[0.2em] mb-2">Striker</div>
                        <div className="text-2xl font-black text-white mb-1">{(isI2 ? liveSc2 : liveSc1).striker || 'Waiting...'}</div>
                        {((isI2 ? liveSc2 : liveSc1).striker) && (
                            <div className="flex gap-4 text-slate-400 font-bold">
                                <span>{(isI2 ? liveSc2 : liveSc1).batsmen[(isI2 ? liveSc2 : liveSc1).striker]?.runs} <span className="text-[10px] opacity-60">R</span></span>
                                <span>{(isI2 ? liveSc2 : liveSc1).batsmen[(isI2 ? liveSc2 : liveSc1).striker]?.balls} <span className="text-[10px] opacity-60">B</span></span>
                            </div>
                        )}
                    </div>

                    {/* VS Divider */}
                    <div className="flex flex-col items-center justify-center p-4">
                        <div className="w-12 h-12 rounded-full border-2 border-slate-800 flex items-center justify-center text-slate-500 font-black italic shadow-inner bg-slate-950">VS</div>
                        <div className="mt-4 flex flex-col items-center">
                            <div className="text-[10px] text-slate-500 font-black uppercase tracking-widest">Curr Over</div>
                            <div className="flex gap-1.5 mt-2">
                                {(isI2 ? liveSc2 : liveSc1).lastSixBalls.map((outcome: any, i: number) => (
                                    <div key={i} className={`w-7 h-7 rounded-sm flex items-center justify-center text-[10px] font-black border ${outcome === 'W' ? 'bg-red-500/20 border-red-500/50 text-red-400' :
                                        outcome === 6 ? 'bg-purple-500/20 border-purple-500/50 text-purple-400' :
                                            outcome === 4 ? 'bg-blue-500/20 border-blue-500/50 text-blue-400' :
                                                outcome === 0 ? 'text-slate-600 border-slate-800' : 'bg-slate-800/50 border-slate-700 text-slate-300'
                                        }`}>
                                        {outcome === 'W' ? 'W' : outcome}
                                    </div>
                                ))}
                                {Array.from({ length: 6 - (isI2 ? liveSc2 : liveSc1).lastSixBalls.length }).map((_, i) => (
                                    <div key={`empty-${i}`} className="w-7 h-7 rounded-sm border border-slate-800/30"></div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Bowler */}
                    <div className="bg-slate-900 p-6 rounded-2xl flex flex-col items-center justify-center text-center">
                        <div className="text-[10px] text-cyan-400 font-black uppercase tracking-[0.2em] mb-2">Bowler</div>
                        <div className="text-2xl font-black text-white mb-1">{(isI2 ? liveSc2 : liveSc1).currentBowler || 'Waiting...'}</div>
                        {((isI2 ? liveSc2 : liveSc1).currentBowler) && (
                            <div className="flex gap-4 text-slate-400 font-bold">
                                <span>{(isI2 ? liveSc2 : liveSc1).bowlers[(isI2 ? liveSc2 : liveSc1).currentBowler]?.wickets} <span className="text-[10px] opacity-60">W</span></span>
                                <span>{(isI2 ? liveSc2 : liveSc1).bowlers[(isI2 ? liveSc2 : liveSc1).currentBowler]?.runs} <span className="text-[10px] opacity-60">R</span></span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Target & RRR Logic for 2nd Innings */}
            {isI2 && !isFinished && (
                <div className="bg-emerald-950/20 border border-emerald-900/30 rounded-2xl p-4 flex flex-col md:flex-row justify-between items-center gap-4">
                    <div className="text-emerald-400 font-black uppercase tracking-widest text-sm">Target: {liveSc1.total_runs + 1}</div>
                    <div className="text-slate-300 font-medium">
                        Need <span className="text-white font-bold">{Math.max(0, (liveSc1.total_runs + 1) - liveSc2.total_runs)}</span> runs from <span className="text-white font-bold">{Math.max(0, 120 - currentI2Balls.length)}</span> balls
                    </div>
                    <div className="bg-slate-950 px-4 py-1.5 rounded-full border border-slate-800 text-xs text-slate-400 font-bold">
                        RRR: {(((liveSc1.total_runs + 1 - liveSc2.total_runs) / Math.max(1, (120 - currentI2Balls.length))) * 6).toFixed(2)}
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {renderScorecard(firstBattingTeamName, liveSc1, !isI2)}
                {renderScorecard(secondBattingTeamName, liveSc2, isI2 && !isFinished)}
            </div>

            {/* ── BOWLING STRATEGY TIMELINE ── */}
            {!isFinished && (
                <div className="bg-slate-950 rounded-3xl p-6 border border-slate-900/50 shadow-2xl">
                    <div className="flex justify-between items-center mb-6">
                        <div className="space-y-1">
                            <h3 className="text-xl font-black text-white uppercase tracking-tighter flex items-center gap-2">
                                <span className="w-1.5 h-6 bg-emerald-500 rounded-full"></span>
                                Bowling Strategy
                            </h3>
                            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest pl-3">Pre-planned Performance-driven sequence</p>
                        </div>
                        <div className="flex gap-4 text-[10px] font-bold uppercase tracking-widest text-slate-500 bg-slate-900/50 px-4 py-2 rounded-full border border-slate-800">
                            <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-emerald-500"></div> PP</div>
                            <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-cyan-500"></div> Mid</div>
                            <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-red-500"></div> Death</div>
                        </div>
                    </div>

                    <div className="flex gap-3 overflow-x-auto pb-6 pt-2 px-1 custom-scrollbar">
                        {(isI2 ? (matchData.bowling_strategy?.team_a) : (matchData.bowling_strategy?.team_b))?.map((bowlerName: string, i: number) => {
                            const currentOverNum = Math.floor((isI2 ? currentI2Balls.length : currentI1Balls.length) / 6);
                            const isCurrent = i === currentOverNum;
                            const isPast = i < currentOverNum;
                            const phase = i < 6 ? 'PP' : i < 15 ? 'MID' : 'DTH';

                            // Color mapping
                            const colors = {
                                'PP': 'emerald',
                                'MID': 'cyan',
                                'DTH': 'red'
                            };
                            const c = colors[phase as keyof typeof colors];

                            return (
                                <div key={i} className={`flex-shrink-0 w-28 p-3 rounded-2xl border transition-all duration-500 ${isCurrent ? `bg-${c}-500/10 border-${c}-500 shadow-[0_0_20px_rgba(var(--tw-shadow-color),0.2)] shadow-${c}-500/20 scale-105 -translate-y-1 z-10` :
                                        isPast ? 'bg-slate-900/30 border-slate-800/50 opacity-30 scale-95' :
                                            'bg-slate-900/80 border-slate-800 hover:border-slate-700'
                                    }`}>
                                    <div className={`text-[9px] font-black uppercase mb-1 tracking-tighter ${isCurrent ? `text-${c}-400` : 'text-slate-500'}`}>
                                        Over {i + 1}
                                    </div>
                                    <div className={`text-[11px] font-black truncate leading-tight ${isCurrent ? 'text-white' : 'text-slate-400'}`}>
                                        {bowlerName.split(' ').pop()}
                                    </div>
                                    <div className={`text-[8px] font-bold mt-1 ${isCurrent ? `text-${c}-500/80` : 'text-slate-600'}`}>
                                        {phase}
                                    </div>
                                    <div className={`mt-2 h-1 w-full rounded-full overflow-hidden bg-slate-800`}>
                                        <div className={`h-full rounded-full transition-all duration-1000 ${isCurrent || isPast ? `bg-${c}-500` : `bg-${c}-500/20`} ${isCurrent ? 'w-full' : isPast ? 'w-full' : 'w-0'}`}></div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            <div className="bg-slate-900 rounded-2xl p-6 border border-slate-800">
                <h3 className="text-xl font-bold text-slate-100 mb-6 flex justify-between">
                    Live Commentary
                    <span className="text-emerald-400 text-sm">{isI2 ? '2nd Innings' : '1st Innings'}</span>
                </h3>
                <div ref={logRef} className="space-y-3 h-96 overflow-y-auto pr-2 custom-scrollbar scroll-smooth">
                    {activeLog.map((ball: any, i: number) => {
                        const isWicket = ball.outcome === 'W';
                        const isBoundary = ball.outcome === 4 || ball.outcome === 6;

                        return (
                            <div key={i} className={`flex gap-4 p-3 rounded-xl border transition-all ${isWicket ? 'bg-red-950/20 border-red-900/30' :
                                isBoundary ? 'bg-emerald-950/20 border-emerald-900/30' :
                                    'bg-slate-950/50 border-slate-800/50'
                                }`}>
                                <div className="font-bold whitespace-nowrap text-slate-400">{ball.over}</div>
                                <div className="flex-1">
                                    <span className="text-slate-300 font-medium">{ball.description.split('-')[0]}</span>
                                    <span className="text-slate-400"> - </span>
                                    <span className={`font-bold ${isWicket ? 'text-red-400' :
                                        isBoundary ? 'text-emerald-400' :
                                            'text-slate-200'
                                        }`}>
                                        {ball.description.split('- ')[1] || ball.description}
                                    </span>
                                </div>
                                <div className="font-mono text-sm text-slate-500 whitespace-nowrap">Score: {ball.score}</div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* ── PIXEL-PERFECT IPL BROADCAST TICKER ── */}
            <div className={`fixed bottom-0 left-0 right-0 z-[100] transition-transform duration-500 ${isFinished ? 'translate-y-full' : 'translate-y-0'} select-none font-sans italic uppercase font-black tracking-tighter`}>
                <div className="bg-black/95 backdrop-blur-sm border-t border-slate-800 p-0 shadow-[0_-15px_50px_-10px_rgba(0,0,0,0.8)]">
                    <div className="max-w-[1400px] mx-auto flex items-stretch h-[70px] border-x border-slate-800 overflow-hidden">

                        {/* 1. Team Names & Event Branding */}
                        <div className="flex flex-col justify-center px-6 bg-white min-w-[200px] text-black border-r border-zinc-100">
                            <div className="text-sm leading-tight">{(isI2 ? secondBattingTeamName : firstBattingTeamName).slice(0, 3)} v <span className="text-zinc-400">{(isI2 ? firstBattingTeamName : secondBattingTeamName).slice(0, 3)}</span></div>
                            <div className="text-[10px] text-[#ed1c24] font-black mt-1 tracking-wider italic">PRANAV SIMULATOR</div>
                        </div>

                        {/* 2. The Trapezoid Score Block */}
                        <div className="relative flex items-stretch translate-x-[-10px] z-10">
                            {/* Score Part (Gold) */}
                            <div
                                className="bg-[#f9d80d] text-black flex items-center justify-center px-8 min-w-[140px]"
                                style={{ clipPath: 'polygon(15% 0, 100% 0, 85% 100%, 0 100%)' }}
                            >
                                <div className="text-3xl">
                                    {(isI2 ? liveSc2 : liveSc1).total_runs}-{(isI2 ? liveSc2 : liveSc1).wickets}
                                </div>
                            </div>
                            {/* Overs Part (Red Accent) */}
                            <div
                                className="bg-[#ed1c24] text-white flex items-center justify-center px-6 ml-[-25px]"
                                style={{ clipPath: 'polygon(20% 0, 100% 0, 80% 100%, 0 100%)' }}
                            >
                                <div className="text-lg">
                                    {Math.floor((isI2 ? liveSc2 : liveSc1).overs)}
                                </div>
                            </div>
                        </div>

                        {/* 3. Dual Batter Rows */}
                        <div className="flex flex-col flex-1 gap-px bg-slate-800 ml-[-20px]">
                            {/* Striker */}
                            <div className="flex-1 bg-[#ed1c24] flex items-center text-white">
                                <div className="w-1.5 h-full bg-white mr-3"></div> {/* Striker Indicator bar */}
                                <div className="flex-1 text-sm truncate pr-2 flex items-center">
                                    <span className="text-yellow-300 mr-1.5">*</span>
                                    {(isI2 ? liveSc2 : liveSc1).striker || '-'}
                                </div>
                                <div className="bg-[#f9d80d] text-black px-4 h-full flex items-center gap-3 min-w-[100px] justify-end">
                                    <span className="text-lg">{(isI2 ? liveSc2 : liveSc1).batsmen[(isI2 ? liveSc2 : liveSc1).striker]?.runs || 0}</span>
                                    <span className="text-[11px] opacity-80 mt-1">{(isI2 ? liveSc2 : liveSc1).batsmen[(isI2 ? liveSc2 : liveSc1).striker]?.balls || 0}</span>
                                </div>
                            </div>
                            {/* Non-Striker */}
                            <div className="flex-1 bg-[#ed1c24] flex items-center text-white opacity-95">
                                <div className="w-1.5 h-full bg-transparent mr-3"></div>
                                <div className="flex-1 text-sm truncate pr-2">{(isI2 ? liveSc2 : liveSc1).nonStriker || '-'}</div>
                                <div className="bg-[#f9d80d] text-black px-4 h-full flex items-center gap-3 min-w-[100px] justify-end">
                                    <span className="text-lg">{(isI2 ? liveSc2 : liveSc1).batsmen[(isI2 ? liveSc2 : liveSc1).nonStriker]?.runs || 0}</span>
                                    <span className="text-[11px] opacity-80 mt-1">{(isI2 ? liveSc2 : liveSc1).batsmen[(isI2 ? liveSc2 : liveSc1).nonStriker]?.balls || 0}</span>
                                </div>
                            </div>
                        </div>

                        {/* 4. Bowler & Ball History */}
                        <div className="flex flex-col min-w-[320px] gap-px bg-slate-800">
                            {/* Bowler Stats */}
                            <div className="flex-1 bg-zinc-900 flex items-center justify-between px-4 text-white border-b border-white/5">
                                <div className="text-sm text-zinc-400">{(isI2 ? liveSc2 : liveSc1).currentBowler || '-'}</div>
                                <div className="flex items-center gap-3">
                                    <div className="text-lg">
                                        {(isI2 ? liveSc2 : liveSc1).bowlers[(isI2 ? liveSc2 : liveSc1).currentBowler]?.wickets || 0}-
                                        {(isI2 ? liveSc2 : liveSc1).bowlers[(isI2 ? liveSc2 : liveSc1).currentBowler]?.runs || 0}
                                    </div>
                                    <div className="text-xs text-zinc-500 mt-1 italic opacity-60">
                                        {(Math.floor((isI2 ? liveSc2 : liveSc1).bowlers[(isI2 ? liveSc2 : liveSc1).currentBowler]?.overs || 0) + ((isI2 ? liveSc2 : liveSc1).bowlers[(isI2 ? liveSc2 : liveSc1).currentBowler]?.overs % 1) * 0.6).toFixed(1)}
                                    </div>
                                </div>
                            </div>
                            {/* Ball History Row */}
                            <div className="flex-1 bg-white flex items-center px-4 gap-2">
                                <div className="w-2 h-2 rounded-full bg-zinc-300"></div> {/* Dot indicator */}
                                <div className="flex gap-1.5 overflow-hidden">
                                    {(isI2 ? liveSc2 : liveSc1).lastSixBalls.map((outcome: any, i: number) => (
                                        <div key={i} className={`flex items-center justify-center font-black italic relative transition-transform duration-300 scale-100 hover:scale-110 ${outcome === 'W' ? 'w-6 h-6 rounded-full bg-[#ed1c24] text-white text-[10px]' :
                                            outcome === 6 || outcome === 4 ? 'w-6 h-6 rounded-full bg-[#f9d80d] text-black text-[10px] border border-black/10' :
                                                'text-zinc-900 text-xs w-5 h-5'
                                            }`}>
                                            {outcome === 'W' ? 'W' : outcome}
                                        </div>
                                    ))}
                                    {Array.from({ length: 6 - (isI2 ? liveSc2 : liveSc1).lastSixBalls.length }).map((_, i) => (
                                        <div key={`empty-${i}`} className="w-5 h-5 rounded-full bg-zinc-50 border border-zinc-100"></div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        {/* 5. Branding Logo */}
                        <div className="bg-white flex items-center px-6 border-l border-zinc-100">
                            <div className="w-10 h-10 bg-[#ed1c24] rounded-full flex items-center justify-center shadow-lg transform -rotate-12 transition-transform hover:rotate-0 cursor-pointer group">
                                <span className="text-white text-2xl font-black italic group-hover:scale-110 transition-transform">P</span>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
}
