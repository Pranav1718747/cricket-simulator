'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import MatchDashboard from '@/components/MatchDashboard';

// ── Helper: auto-select a balanced XI from a player pool ─────────────────────
function autoSelectXI(pool: any[], exclude: any[]): any[] {
    const excludeIds = new Set(exclude.map((p: any) => p.id));
    const available = pool.filter(p => !excludeIds.has(p.id));

    const sorted = [...available].sort((a, b) => b.star_rating - a.star_rating);

    const wks = sorted.filter(p => p.role === 'Wicketkeeper');
    const bowls = sorted.filter(p => p.role === 'Bowler');
    const ars = sorted.filter(p => p.role === 'All-rounder');
    const bats = sorted.filter(p => p.role === 'Batsman');

    const selected: any[] = [];

    // 1 WK
    if (wks.length > 0) selected.push(wks[0]);

    // 4 bowlers (mix pacers + spinners)
    const pacers = bowls.filter(p => p.bowling_style && !p.bowling_style.includes('Spinner'));
    const spinners = bowls.filter(p => p.bowling_style && p.bowling_style.includes('Spinner'));
    const alreadyIds = () => new Set(selected.map(p => p.id));

    let pCount = 0, sCount = 0;
    for (const p of pacers) {
        if (!alreadyIds().has(p.id) && pCount < 2) { selected.push(p); pCount++; }
    }
    for (const p of spinners) {
        if (!alreadyIds().has(p.id) && sCount < 2) { selected.push(p); sCount++; }
    }
    // fill remaining bowler spots
    for (const p of bowls) {
        if (selected.length >= 5) break;
        if (!alreadyIds().has(p.id)) selected.push(p);
    }

    // 2 all-rounders
    let arCount = 0;
    for (const p of ars) {
        if (selected.length >= 7) break;
        if (!alreadyIds().has(p.id) && arCount < 2) { selected.push(p); arCount++; }
    }

    // Fill rest with batsmen up to 11
    for (const p of bats) {
        if (selected.length >= 11) break;
        if (!alreadyIds().has(p.id)) selected.push(p);
    }

    // Final fill from anyone
    for (const p of sorted) {
        if (selected.length >= 11) break;
        if (!alreadyIds().has(p.id)) selected.push(p);
    }

    return selected.slice(0, 11);
}

// ── Toss Modal ────────────────────────────────────────────────────────────────
function TossModal({ teamA, teamB, onDone }: { teamA: string, teamB: string, onDone: (winner: string, choice: string) => void }) {
    const [phase, setPhase] = useState<'flip' | 'decide' | 'result'>('flip');
    const [coinFace, setCoinFace] = useState('🟡');
    const [tossWinner, setTossWinner] = useState('');
    const [tossChoice, setTossChoice] = useState('');

    useEffect(() => {
        // Animate coin flipping
        let count = 0;
        const faces = ['🟡', '⚪'];
        const interval = setInterval(() => {
            setCoinFace(faces[count % 2]);
            count++;
            if (count > 12) {
                clearInterval(interval);
                const winner = Math.random() < 0.5 ? teamA : teamB;
                setTossWinner(winner);
                setPhase('decide');
            }
        }, 150);
        return () => clearInterval(interval);
    }, [teamA, teamB]);

    const handleChoice = (choice: string) => {
        setTossChoice(choice);
        setPhase('result');
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
            <div className="bg-slate-900 border border-slate-700 rounded-3xl p-12 text-center max-w-md w-full mx-4 shadow-2xl">
                <h2 className="text-3xl font-black text-white mb-8">⚡ Toss Time!</h2>

                {phase === 'flip' && (
                    <div>
                        <div className="text-8xl mb-6 animate-bounce">{coinFace}</div>
                        <p className="text-slate-400 text-lg animate-pulse">Flipping the coin...</p>
                    </div>
                )}

                {phase === 'decide' && (
                    <div className="space-y-6 animate-in fade-in zoom-in duration-300">
                        <div className="text-7xl">🪙</div>
                        <div>
                            <div className="text-2xl font-black text-emerald-400">{tossWinner}</div>
                            <div className="text-slate-400 text-lg mt-1">wins the toss! What to do?</div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <button
                                onClick={() => handleChoice('Bat')}
                                className="py-4 bg-slate-800 hover:bg-emerald-500/20 hover:border-emerald-500/50 border border-slate-700 text-white font-black text-xl rounded-2xl transition-all"
                            >
                                🏏 Bat
                            </button>
                            <button
                                onClick={() => handleChoice('Bowl')}
                                className="py-4 bg-slate-800 hover:bg-cyan-500/20 hover:border-cyan-500/50 border border-slate-700 text-white font-black text-xl rounded-2xl transition-all"
                            >
                                🥎 Bowl
                            </button>
                        </div>
                    </div>
                )}

                {phase === 'result' && (
                    <div className="space-y-6 animate-in fade-in zoom-in duration-300">
                        <div className="text-7xl">🏏</div>
                        <div>
                            <div className="text-2xl font-black text-emerald-400">{tossWinner}</div>
                            <div className="text-slate-400 text-lg mt-1">wins the toss!</div>
                        </div>
                        <div className="bg-slate-800 rounded-2xl px-8 py-4 border border-emerald-500/20">
                            <span className="text-slate-400">chose to </span>
                            <span className="text-yellow-400 font-black text-xl">{tossChoice} first</span>
                        </div>
                        <button
                            onClick={() => onDone(tossWinner, tossChoice)}
                            className="w-full py-4 bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-black text-lg rounded-2xl hover:scale-105 transition-all shadow-lg shadow-emerald-500/20 border border-white/10"
                        >
                            Start Match 🚀
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export default function SimulatePage() {
    const [players, setPlayers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    const [teamA, setTeamA] = useState<any[]>([]);
    const [teamB, setTeamB] = useState<any[]>([]);
    const [teamAName, setTeamAName] = useState('Team A');
    const [teamBName, setTeamBName] = useState('Team B');
    const [searchQuery, setSearchQuery] = useState('');

    const [pitchType, setPitchType] = useState('Balanced');
    const [dewFactor, setDewFactor] = useState(false);

    const [showToss, setShowToss] = useState(false);
    const [tossResult, setTossResult] = useState<{ winner: string; choice: string } | null>(null);
    const [simulating, setSimulating] = useState(false);
    const [matchResult, setMatchResult] = useState<any>(null);

    useEffect(() => { fetchPlayers(); }, []);

    const fetchPlayers = async () => {
        try {
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await axios.get(`${baseUrl}/api/players/`);
            setPlayers(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // ── Auto Generate XI ─────────────────────────────────────────────────────
    const autoGenerateA = () => {
        const xi = autoSelectXI(players, teamB);
        setTeamA(xi);
    };

    const autoGenerateB = () => {
        const xi = autoSelectXI(players, teamA);
        setTeamB(xi);
    };

    const autoGenerateBoth = () => {
        const xiA = autoSelectXI(players, []);
        const xiB = autoSelectXI(players, xiA);
        setTeamA(xiA);
        setTeamB(xiB);
    };

    // ── Player selection ─────────────────────────────────────────────────────
    const handleSelect = (p: any, team: 'A' | 'B') => {
        if (team === 'A' && teamA.length < 11 && !teamA.find(x => x.id === p.id)) {
            setTeamA([...teamA, p]);
        } else if (team === 'B' && teamB.length < 11 && !teamB.find(x => x.id === p.id)) {
            setTeamB([...teamB, p]);
        }
    };

    const removePlayer = (id: number, team: 'A' | 'B') => {
        if (team === 'A') setTeamA(teamA.filter(p => p.id !== id));
        else setTeamB(teamB.filter(p => p.id !== id));
    };

    // ── Toss → Simulate flow ─────────────────────────────────────────────────
    const handlePlayClick = () => {
        if (teamA.length < 11 || teamB.length < 11) {
            alert("Both teams must have exactly 11 players!");
            return;
        }
        setShowToss(true);
    };

    const handleTossDone = async (winner: string, choice: string) => {
        setShowToss(false);
        setTossResult({ winner, choice });
        await runSimulation(winner, choice);
    };

    const runSimulation = async (wonBy?: string, chosen?: string) => {
        setSimulating(true);
        setMatchResult(null);
        try {
            // Determine who bats first based on toss
            let battingFirst = 'team_a';
            const winner = wonBy || (tossResult ? tossResult.winner : null);
            const choice = chosen || (tossResult ? tossResult.choice : null);

            if (winner) {
                const isWinnerA = winner === teamAName;
                const choseBat = choice === 'Bat';

                if (isWinnerA) {
                    battingFirst = choseBat ? 'team_a' : 'team_b';
                } else {
                    battingFirst = choseBat ? 'team_b' : 'team_a';
                }
            }

            const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

            const resA = await axios.post(`${baseUrl}/api/teams/`, {
                name: teamAName,
                player_ids: teamA.map(p => p.id)
            });
            const resB = await axios.post(`${baseUrl}/api/teams/`, {
                name: teamBName,
                player_ids: teamB.map(p => p.id)
            });
            const simRes = await axios.post(`${baseUrl}/api/matches/simulate/`, {
                team_a_id: resA.data.id,
                team_b_id: resB.data.id,
                player_ids_a: teamA.map(p => p.id),
                player_ids_b: teamB.map(p => p.id),
                batting_first: battingFirst,
                pitch_type: pitchType,
                dew_factor: dewFactor
            });
            setMatchResult(simRes.data);
        } catch (err) {
            console.error(err);
            alert("Simulation failed.");
        } finally {
            setSimulating(false);
        }
    };

    if (loading) return <div className="py-20 text-center animate-pulse">Loading engine...</div>;

    return (
        <div className="space-y-8 animate-in fade-in duration-500">

            {/* Toss Modal */}
            {showToss && (
                <TossModal teamA={teamAName} teamB={teamBName} onDone={handleTossDone} />
            )}

            {/* Loading overlay after toss */}
            {simulating && (
                <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm gap-6">
                    <div className="text-6xl animate-spin">🏏</div>
                    <p className="text-white text-2xl font-black animate-pulse">Simulating Match...</p>
                    {tossResult && (
                        <p className="text-slate-400">
                            {tossResult.winner} won the toss and chose to {tossResult.choice} first
                        </p>
                    )}
                </div>
            )}

            {matchResult ? (
                <MatchDashboard matchData={matchResult} />
            ) : (
                <>
                    <div className="text-center space-y-4 mb-8">
                        <h1 className="text-4xl md:text-5xl font-black bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">
                            Match Simulator
                        </h1>
                        <p className="text-slate-400 max-w-xl mx-auto">
                            Build your squads manually or auto-generate balanced teams. Toss decides who bats first!
                        </p>

                        {/* Auto Generate BOTH button */}
                        <button
                            onClick={autoGenerateBoth}
                            className="mt-2 px-6 py-3 bg-gradient-to-r from-violet-500 to-purple-600 text-white font-black rounded-2xl hover:scale-105 transition-all shadow-lg shadow-purple-500/20 text-sm uppercase tracking-widest"
                        >
                            ⚡ Auto Generate Both XIs
                        </button>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                        {/* Roster Pool */}
                        <div className="bg-slate-900 rounded-2xl p-6 border border-slate-800 lg:h-[800px] flex flex-col">
                            <div className="mb-4">
                                <h2 className="text-xl font-bold mb-3 text-slate-100 flex items-center justify-between">
                                    Player Pool
                                    <span className="text-xs bg-slate-800 px-2 py-1 rounded-full text-slate-400">{players.length} Total</span>
                                </h2>
                                <input
                                    type="text"
                                    placeholder="Search players by name..."
                                    className="bg-slate-800 border border-slate-700 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block w-full p-2.5 outline-none placeholder-slate-500"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                            </div>
                            <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
                                {players.filter(p => p.name.toLowerCase().includes(searchQuery.toLowerCase())).map(p => {
                                    const inA = teamA.some(x => x.id === p.id);
                                    const inB = teamB.some(x => x.id === p.id);
                                    const isPicked = inA || inB;

                                    return (
                                        <div key={p.id} className={`p-3 rounded-xl border transition-all ${isPicked ? 'bg-slate-950 border-slate-900 opacity-50' : 'bg-slate-800 border-slate-700 hover:border-slate-500 hover:bg-slate-800/80'}`}>
                                            <div className="flex justify-between items-start mb-2">
                                                <div>
                                                    <div className="font-bold text-sm text-slate-200">{p.name}</div>
                                                    <div className="text-xs text-yellow-500 mb-0.5">{'★'.repeat(Math.floor(p.star_rating || 0))}{p.star_rating % 1 > 0 ? '½' : ''}</div>
                                                    <div className="text-[10px] text-slate-500 flex gap-2">
                                                        <span className="text-cyan-500/80">{p.role}</span>
                                                        <span>{p.tactical_role}</span>
                                                        {p.bowling_style !== 'None' && <span>• {p.bowling_style}</span>}
                                                    </div>
                                                </div>
                                                {!isPicked && (
                                                    <div className="flex gap-1">
                                                        <button onClick={() => handleSelect(p, 'A')} className="px-2 py-1 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 rounded text-xs font-bold transition-colors">A</button>
                                                        <button onClick={() => handleSelect(p, 'B')} className="px-2 py-1 bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 rounded text-xs font-bold transition-colors">B</button>
                                                    </div>
                                                )}
                                                {isPicked && (
                                                    <div className="text-xs font-bold text-slate-600 px-2">{inA ? 'Team A' : 'Team B'}</div>
                                                )}
                                            </div>
                                            <div className="grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-slate-700/50">
                                                <div className="text-[10px]">
                                                    <div className="flex justify-between"><span className="text-slate-500">Power:</span><span className={p.batting_power >= 80 ? 'text-emerald-400 font-bold' : 'text-slate-300'}>{p.batting_power}</span></div>
                                                    <div className="flex justify-between"><span className="text-slate-500">Consist:</span><span className={p.batting_consistency >= 80 ? 'text-emerald-400 font-bold' : 'text-slate-300'}>{p.batting_consistency}</span></div>
                                                </div>
                                                <div className="text-[10px] border-l border-slate-700/50 pl-2">
                                                    <div className="flex justify-between"><span className="text-slate-500">Powerply:</span><span className={p.powerplay_skill >= 80 ? 'text-cyan-400 font-bold' : 'text-slate-300'}>{p.powerplay_skill}</span></div>
                                                    <div className="flex justify-between"><span className="text-slate-500">DeathBrl:</span><span className={p.death_bowling_skill >= 80 ? 'text-cyan-400 font-bold' : 'text-slate-300'}>{p.death_bowling_skill}</span></div>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Team A */}
                        <div className="bg-slate-900/50 rounded-2xl p-6 border border-emerald-500/20 flex flex-col shadow-[0_0_50px_-12px_rgba(52,211,153,0.1)]">
                            <input
                                value={teamAName}
                                onChange={e => setTeamAName(e.target.value)}
                                className="bg-transparent text-2xl font-bold text-emerald-400 border-b border-emerald-500/30 pb-2 mb-3 outline-none focus:border-emerald-400 px-2 transition-all rounded-t-lg"
                            />
                            <div className="flex items-center justify-between mb-4 px-2">
                                <div className="text-sm font-medium text-slate-400">
                                    Players: <span className={teamA.length === 11 ? 'text-emerald-400 font-bold' : 'text-slate-100'}>{teamA.length}/11</span>
                                </div>
                                <div className="flex gap-2">
                                    {teamA.length > 0 && (
                                        <button
                                            onClick={() => setTeamA([])}
                                            className="text-xs px-3 py-1.5 bg-red-500/10 text-red-400 hover:bg-red-500/20 rounded-lg font-bold transition-colors"
                                        >
                                            Clear
                                        </button>
                                    )}
                                    <button
                                        onClick={autoGenerateA}
                                        className="text-xs px-3 py-1.5 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 rounded-lg font-bold transition-colors border border-emerald-500/20"
                                    >
                                        ⚡ Auto XI
                                    </button>
                                </div>
                            </div>
                            <div className="flex-1 overflow-y-auto space-y-2 pr-2">
                                {teamA.map((p, i) => (
                                    <div key={p.id} className="p-3 bg-slate-950 border border-emerald-900/50 rounded-xl flex justify-between items-center group">
                                        <div className="flex items-center gap-3">
                                            <span className="text-slate-600 text-xs w-4">{i + 1}</span>
                                            <div>
                                                <div className="font-bold text-sm text-slate-200">{p.name}</div>
                                                <div className="text-[10px] text-slate-500 flex gap-1">
                                                    <span className="text-yellow-500">{'★'.repeat(Math.floor(p.star_rating || 0))}</span>
                                                    <span className="text-cyan-500/70">{p.role}</span>
                                                    {p.bowling_style && p.bowling_style !== 'None' && <span>• {p.bowling_style}</span>}
                                                </div>
                                            </div>
                                        </div>
                                        <button onClick={() => removePlayer(p.id, 'A')} className="text-slate-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity text-lg">✕</button>
                                    </div>
                                ))}
                                {teamA.length === 0 && (
                                    <div className="h-60 flex flex-col items-center justify-center text-slate-600 text-sm border-2 border-dashed border-slate-800 rounded-xl gap-3">
                                        <span>Add players from the pool</span>
                                        <button onClick={autoGenerateA} className="px-4 py-2 bg-emerald-500/10 text-emerald-400 rounded-lg text-xs font-bold hover:bg-emerald-500/20 border border-emerald-500/20 transition-colors">
                                            or ⚡ Auto Generate
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Team B */}
                        <div className="bg-slate-900/50 rounded-2xl p-6 border border-cyan-500/20 flex flex-col shadow-[0_0_50px_-12px_rgba(34,211,238,0.1)]">
                            <input
                                value={teamBName}
                                onChange={e => setTeamBName(e.target.value)}
                                className="bg-transparent text-2xl font-bold text-cyan-400 border-b border-cyan-500/30 pb-2 mb-3 outline-none focus:border-cyan-400 px-2 transition-all rounded-t-lg"
                            />
                            <div className="flex items-center justify-between mb-4 px-2">
                                <div className="text-sm font-medium text-slate-400">
                                    Players: <span className={teamB.length === 11 ? 'text-cyan-400 font-bold' : 'text-slate-100'}>{teamB.length}/11</span>
                                </div>
                                <div className="flex gap-2">
                                    {teamB.length > 0 && (
                                        <button
                                            onClick={() => setTeamB([])}
                                            className="text-xs px-3 py-1.5 bg-red-500/10 text-red-400 hover:bg-red-500/20 rounded-lg font-bold transition-colors"
                                        >
                                            Clear
                                        </button>
                                    )}
                                    <button
                                        onClick={autoGenerateB}
                                        className="text-xs px-3 py-1.5 bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 rounded-lg font-bold transition-colors border border-cyan-500/20"
                                    >
                                        ⚡ Auto XI
                                    </button>
                                </div>
                            </div>
                            <div className="flex-1 overflow-y-auto space-y-2 pr-2">
                                {teamB.map((p, i) => (
                                    <div key={p.id} className="p-3 bg-slate-950 border border-cyan-900/50 rounded-xl flex justify-between items-center group">
                                        <div className="flex items-center gap-3">
                                            <span className="text-slate-600 text-xs w-4">{i + 1}</span>
                                            <div>
                                                <div className="font-bold text-sm text-slate-200">{p.name}</div>
                                                <div className="text-[10px] text-slate-500 flex gap-1">
                                                    <span className="text-yellow-500">{'★'.repeat(Math.floor(p.star_rating || 0))}</span>
                                                    <span className="text-cyan-500/70">{p.role}</span>
                                                    {p.bowling_style && p.bowling_style !== 'None' && <span>• {p.bowling_style}</span>}
                                                </div>
                                            </div>
                                        </div>
                                        <button onClick={() => removePlayer(p.id, 'B')} className="text-slate-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity text-lg">✕</button>
                                    </div>
                                ))}
                                {teamB.length === 0 && (
                                    <div className="h-60 flex flex-col items-center justify-center text-slate-600 text-sm border-2 border-dashed border-slate-800 rounded-xl gap-3">
                                        <span>Add players from the pool</span>
                                        <button onClick={autoGenerateB} className="px-4 py-2 bg-cyan-500/10 text-cyan-400 rounded-lg text-xs font-bold hover:bg-cyan-500/20 border border-cyan-500/20 transition-colors">
                                            or ⚡ Auto Generate
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>

                    </div>

                    {/* Match Conditions */}
                    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 mt-8 shadow-lg max-w-4xl mx-auto">
                        <h3 className="text-xl font-bold text-slate-200 mb-4 text-center">Match Conditions</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center justify-center">
                            <div className="flex flex-col items-center">
                                <label className="text-sm text-slate-400 mb-2 font-bold uppercase tracking-widest">Pitch Type</label>
                                <div className="flex gap-2">
                                    {['Balanced', 'Batting', 'Pace', 'Spin'].map(type => (
                                        <button
                                            key={type}
                                            onClick={() => setPitchType(type)}
                                            className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${pitchType === type ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                                        >
                                            {type}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div className="flex flex-col items-center">
                                <label className="text-sm text-slate-400 mb-2 font-bold uppercase tracking-widest">Weather</label>
                                <button
                                    onClick={() => setDewFactor(!dewFactor)}
                                    className={`px-6 py-2 rounded-xl text-sm font-bold transition-all flex items-center gap-2 ${dewFactor ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                                >
                                    💧 {dewFactor ? 'Heavy Dew (Death Bowling Nerf)' : 'Dry Outfield'}
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Play Button */}
                    <div className="text-center pt-8 border-t border-slate-800 mt-8">
                        <button
                            disabled={simulating || teamA.length !== 11 || teamB.length !== 11}
                            onClick={handlePlayClick}
                            className={`px-10 py-5 rounded-full text-xl font-black uppercase tracking-widest transition-all ${teamA.length === 11 && teamB.length === 11 && !simulating
                                ? 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-white hover:scale-105 shadow-[0_0_40px_-5px_var(--tw-shadow-color)] shadow-emerald-500'
                                : 'bg-slate-800 text-slate-500 cursor-not-allowed'
                                }`}
                        >
                            🏏 Toss &amp; Play
                        </button>
                        {(teamA.length !== 11 || teamB.length !== 11) && (
                            <p className="text-slate-600 text-sm mt-3">
                                {teamA.length < 11 && `Team A needs ${11 - teamA.length} more. `}
                                {teamB.length < 11 && `Team B needs ${11 - teamB.length} more.`}
                            </p>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
