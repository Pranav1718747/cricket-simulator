'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';

interface Player {
    id: number;
    name: string;
    country: string;
    role: string;
    tactical_role: string;
    bowling_style: string;
    batting_avg: number;
    strike_rate: number;
    bowling_avg: number;
    economy: number;

    // V2 Attributes
    batting_power: number;
    batting_consistency: number;
    spin_skill: number;
    pace_skill: number;
    powerplay_skill: number;
    middle_overs_skill: number;
    death_bowling_skill: number;
    fielding_skill: number;

    form_rating: number;
    star_rating: number;
}

export default function PlayersPage() {
    const [players, setPlayers] = useState<Player[]>([]);
    const [loading, setLoading] = useState(true);
    const [roleFilter, setRoleFilter] = useState('');
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        fetchPlayers();
    }, [roleFilter]);

    const fetchPlayers = async () => {
        setLoading(true);
        try {
            const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const url = roleFilter ? `${baseUrl}/api/players/?role=${roleFilter}` : `${baseUrl}/api/players/`;
            const res = await axios.get(url);
            setPlayers(res.data);
        } catch (err) {
            console.error("Failed to fetch players", err);
        } finally {
            setLoading(false);
        }
    };

    const filteredPlayers = players.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col md:flex-row md:justify-between md:items-center space-y-4 md:space-y-0 border-b border-slate-800 pb-4">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-500 bg-clip-text text-transparent">Player Database</h1>

                <div className="flex space-x-4">
                    <input
                        type="text"
                        placeholder="Search players..."
                        className="bg-slate-800 border-slate-700 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 outline-none placeholder-slate-500 w-full md:w-64"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    <select
                        className="bg-slate-800 border-slate-700 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 outline-none"
                        value={roleFilter}
                        onChange={(e) => setRoleFilter(e.target.value)}
                    >
                        <option value="">All Roles</option>
                        <option value="Batsman">Batsman</option>
                        <option value="Bowler">Bowler</option>
                        <option value="All-rounder">All-rounder</option>
                        <option value="Wicketkeeper">Wicketkeeper</option>
                    </select>
                </div>
            </div>

            {loading ? (
                <div className="text-center py-20 text-slate-500 animate-pulse">Loading amazing players...</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredPlayers.map(player => (
                        <div key={player.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:shadow-lg hover:border-slate-700 transition-all group">
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <h3 className="text-xl font-bold text-slate-100 group-hover:text-emerald-400 transition-colors">{player.name}</h3>
                                    <div className="flex items-center space-x-1 mt-1 mb-1">
                                        <span className="text-yellow-400 text-sm">{'★'.repeat(Math.floor(player.star_rating || 0))}{player.star_rating % 1 > 0 ? '½' : ''}</span>
                                        <span className="text-xs text-slate-500 ml-1">({player.star_rating})</span>
                                    </div>
                                    <div className="flex items-center space-x-2 text-sm text-slate-400 mt-1">
                                        <span className="bg-slate-800 px-2 py-0.5 rounded text-xs">{player.country}</span>
                                        <span className="text-cyan-500/80">{player.role}</span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-2xl font-black text-emerald-500/50">{player.form_rating.toFixed(1)}</div>
                                    <div className="text-[10px] text-slate-500 uppercase tracking-widest">FORM</div>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4 mt-6">
                                {/* Batting Attributes */}
                                <div className="bg-slate-950 rounded-xl p-3 border border-slate-800/50">
                                    <div className="flex justify-between items-center mb-2 pb-1 border-b border-slate-800">
                                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Batting</div>
                                        <div className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-300">{player.tactical_role}</div>
                                    </div>
                                    <div className="space-y-1.5 mt-2">
                                        <div className="flex justify-between text-sm">
                                            <span className="text-slate-500 text-xs">Power</span>
                                            <span className={`font-mono font-bold ${player.batting_power >= 80 ? 'text-emerald-400' : player.batting_power >= 60 ? 'text-yellow-400' : 'text-slate-400'}`}>{player.batting_power}</span>
                                        </div>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-slate-500 text-xs">Consistency</span>
                                            <span className={`font-mono font-bold ${player.batting_consistency >= 80 ? 'text-emerald-400' : player.batting_consistency >= 60 ? 'text-yellow-400' : 'text-slate-400'}`}>{player.batting_consistency}</span>
                                        </div>
                                        <div className="flex justify-between text-sm pt-1 border-t border-slate-800/50">
                                            <span className="text-slate-500 text-xs">vs Spin / Pace</span>
                                            <span className="font-mono text-xs text-slate-300">{player.spin_skill} / {player.pace_skill}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Bowling Attributes */}
                                <div className="bg-slate-950 rounded-xl p-3 border border-slate-800/50">
                                    <div className="flex justify-between items-center mb-2 pb-1 border-b border-slate-800">
                                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Bowling</div>
                                        {player.bowling_style !== 'None' && (
                                            <div className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-cyan-400 max-w-[80px] truncate" title={player.bowling_style}>{player.bowling_style}</div>
                                        )}
                                    </div>
                                    <div className="space-y-1.5 mt-2">
                                        <div className="flex justify-between text-sm">
                                            <span className="text-slate-500 text-xs text-left">Powerplay</span>
                                            <span className={`font-mono font-bold ${player.powerplay_skill >= 80 ? 'text-cyan-400' : player.powerplay_skill >= 60 ? 'text-yellow-400' : 'text-slate-400'}`}>{player.powerplay_skill}</span>
                                        </div>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-slate-500 text-xs">Middle</span>
                                            <span className={`font-mono font-bold ${player.middle_overs_skill >= 80 ? 'text-cyan-400' : player.middle_overs_skill >= 60 ? 'text-yellow-400' : 'text-slate-400'}`}>{player.middle_overs_skill}</span>
                                        </div>
                                        <div className="flex justify-between text-sm">
                                            <span className="text-slate-500 text-xs">Death</span>
                                            <span className={`font-mono font-bold ${player.death_bowling_skill >= 80 ? 'text-cyan-400' : player.death_bowling_skill >= 60 ? 'text-yellow-400' : 'text-slate-400'}`}>{player.death_bowling_skill}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="mt-3 pt-3 border-t border-slate-800/50 flex justify-between items-center px-1">
                                <div className="text-xs text-slate-500">Real Stats</div>
                                <div className="text-xs text-slate-400 font-mono space-x-3">
                                    <span title="Batting Average">AVG: {player.batting_avg > 0 ? player.batting_avg : '-'}</span>
                                    <span title="Strike Rate">SR: {player.strike_rate > 0 ? player.strike_rate : '-'}</span>
                                    <span title="Economy">ECO: {player.economy > 0 ? player.economy : '-'}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
