import React, { useState, useEffect } from 'react';
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Legend } from 'recharts';
import { Link } from 'react-router-dom';
import client from '../api/client';

const SEASONS = [
  2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016,
  2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005
];

export default function Compare() {
  const [season1, setSeason1] = useState(2025);
  const [season2, setSeason2] = useState(2025);
  const [leaderboard1, setLeaderboard1] = useState([]);
  const [leaderboard2, setLeaderboard2] = useState([]);
  const [player1Id, setPlayer1Id] = useState('');
  const [player2Id, setPlayer2Id] = useState('');
  const [player1Data, setPlayer1Data] = useState(null);
  const [player2Data, setPlayer2Data] = useState(null);
  const [h2h, setH2h] = useState(null);

  useEffect(() => {
    if (player1Id && player2Id && player1Data && player2Data) {
      client.get(`/predictions/head-to-head/${player1Id}/${season1}/${player2Id}/${season2}`)
        .then(res => setH2h(res.data));
    }
  }, [player1Data, player2Data]);

  useEffect(() => {
    client.get(`/leaderboard/mvp/${season1}`).then(res => {
      setLeaderboard1(res.data);
      setPlayer1Id('');
      setPlayer1Data(null);
    });
  }, [season1]);

  useEffect(() => {
    client.get(`/leaderboard/mvp/${season2}`).then(res => {
      setLeaderboard2(res.data);
      setPlayer2Id('');
      setPlayer2Data(null);
    });
  }, [season2]);

  useEffect(() => {
    if (player1Id) {
      client.get(`/predictions/${player1Id}/${season1}`)
        .then(res => setPlayer1Data(res.data));
    }
  }, [player1Id, season1]);

  useEffect(() => {
    if (player2Id) {
      client.get(`/predictions/${player2Id}/${season2}`)
        .then(res => setPlayer2Data(res.data));
    }
  }, [player2Id, season2]);

  const buildRadarData = (p1, p2) => {
    if (!p1 || !p2) return [];
    const normalize = (val, max) => Math.min(100, Math.round((val / max) * 100));
    return [
      { stat: 'PPG', p1: normalize(p1.points_per_game, 40), p2: normalize(p2.points_per_game, 40) },
      { stat: 'TS%', p1: normalize(p1.ts_pct, 0.7), p2: normalize(p2.ts_pct, 0.7) },
      { stat: 'Usage', p1: normalize(p1.usage_rate, 0.4), p2: normalize(p2.usage_rate, 0.4) },
      { stat: 'Win%', p1: normalize(p1.team_win_pct, 1), p2: normalize(p2.team_win_pct, 1) },
      { stat: 'Games', p1: normalize(p1.games_played, 82), p2: normalize(p2.games_played, 82) },
      { stat: 'PIE', p1: normalize(p1.per, 0.25), p2: normalize(p2.per, 0.25) },
    ];
  };

  const p1Name = leaderboard1.find(p => p.player_id === parseInt(player1Id))?.full_name;
  const p2Name = leaderboard2.find(p => p.player_id === parseInt(player2Id))?.full_name;
  const radarData = buildRadarData(player1Data, player2Data);

  const selectStyle = (color) => ({
    padding: '8px 16px',
    backgroundColor: '#1a1a2e',
    color: 'white',
    border: `1px solid ${color}`,
    borderRadius: '4px',
    minWidth: '200px'
  });

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <h1 style={{ color: '#e94560' }}>Compare Players</h1>

      <div style={{ display: 'flex', gap: '32px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <select value={season1} onChange={e => setSeason1(Number(e.target.value))} style={selectStyle('#4a90d9')}>
            {SEASONS.map(s => (
              <option key={s} value={s}>{s - 1}-{String(s).slice(2)}</option>
            ))}
          </select>
          <select value={player1Id} onChange={e => setPlayer1Id(e.target.value)} style={selectStyle('#4a90d9')}>
            <option value="">Select Player 1</option>
            {leaderboard1.map(p => (
              <option key={p.player_id} value={p.player_id}>{p.full_name}</option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <select value={season2} onChange={e => setSeason2(Number(e.target.value))} style={selectStyle('#e94560')}>
            {SEASONS.map(s => (
              <option key={s} value={s}>{s - 1}-{String(s).slice(2)}</option>
            ))}
          </select>
          <select value={player2Id} onChange={e => setPlayer2Id(e.target.value)} style={selectStyle('#e94560')}>
            <option value="">Select Player 2</option>
            {leaderboard2.map(p => (
              <option key={p.player_id} value={p.player_id}>{p.full_name}</option>
            ))}
          </select>
        </div>
      </div>

      {player1Data && player2Data && (
        <>
          <ResponsiveContainer width="100%" height={350}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#333" />
              <PolarAngleAxis dataKey="stat" stroke="white" />
              <Radar name={p1Name} dataKey="p1" stroke="#4a90d9" fill="#4a90d9" fillOpacity={0.3} />
              <Radar name={p2Name} dataKey="p2" stroke="#e94560" fill="#e94560" fillOpacity={0.3} />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginTop: '24px' }}>
            {[
              { data: player1Data, name: p1Name, id: player1Id, color: '#4a90d9' },
              { data: player2Data, name: p2Name, id: player2Id, color: '#e94560' }
            ].map(({ data, name, id, color }) => (
              <div key={id} style={{
                backgroundColor: '#1a1a2e',
                borderRadius: '8px',
                padding: '20px',
                border: `1px solid ${color}`
              }}>
                <Link to={`/player/${id}`} style={{ color, textDecoration: 'none', fontSize: '18px', fontWeight: 'bold' }}>
                  {name}
                </Link>
                <p style={{ color: '#aaa', margin: '4px 0 16px' }}>{data.season}</p>
                {[
                  ['PPG', data.points_per_game],
                  ['APG', data.assists_per_game],
                  ['RPG', data.rebounds_per_game],
                  ['Games Played', data.games_played],
                  ['Team Win%', data.team_win_pct ? (data.team_win_pct * 100).toFixed(1) + '%' : '-'],
                  ['TS%', data.ts_pct ? (data.ts_pct * 100).toFixed(1) + '%' : '-'],
                  ['MVP Rank', data.mvp_rank ? `#${data.mvp_rank}` : 'Not voted'],
                  ['MVP Winner', data.mvp_winner ? '🏆 Yes' : 'No'],
                ].map(([label, value]) => (
                  <div key={label} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    padding: '6px 0',
                    borderBottom: '1px solid #333'
                  }}>
                    <span style={{ color: '#aaa' }}>{label}</span>
                    <span style={{ color: 'white' }}>{value ?? '-'}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>

          {h2h && (
            <div style={{
              marginTop: '32px',
              backgroundColor: '#1a1a2e',
              borderRadius: '8px',
              padding: '24px',
              border: '1px solid #333',
              textAlign: 'center'
            }}>
              <h2 style={{ color: '#aaa', fontWeight: 'normal', marginBottom: '24px' }}>
                Head to Head — Who Wins MVP?
              </h2>

              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', justifyContent: 'center', marginBottom: '24px' }}>
                <span style={{ color: '#4a90d9', fontSize: '18px', fontWeight: 'bold', minWidth: '180px', textAlign: 'right' }}>
                  {h2h.player1.name}
                </span>
                <span style={{ color: '#aaa' }}>{h2h.player1.season}</span>
                <span style={{ color: '#555', fontSize: '20px' }}>vs</span>
                <span style={{ color: '#aaa' }}>{h2h.player2.season}</span>
                <span style={{ color: '#e94560', fontSize: '18px', fontWeight: 'bold', minWidth: '180px', textAlign: 'left' }}>
                  {h2h.player2.name}
                </span>
              </div>

              <div style={{ display: 'flex', borderRadius: '8px', overflow: 'hidden', height: '32px', marginBottom: '12px' }}>
                <div style={{ width: `${h2h.player1.share}%`, backgroundColor: '#4a90d9', transition: 'width 0.5s' }} />
                <div style={{ width: `${h2h.player2.share}%`, backgroundColor: '#e94560', transition: 'width 0.5s' }} />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
                <span style={{ color: '#4a90d9', fontWeight: 'bold' }}>{h2h.player1.share}%</span>
                <span style={{ color: '#e94560', fontWeight: 'bold' }}>{h2h.player2.share}%</span>
              </div>

              <div style={{ fontSize: '20px', color: 'white' }}>
                🏆 <span style={{
                  color: h2h.winner === h2h.player1.name ? '#4a90d9' : '#e94560',
                  fontWeight: 'bold'
                }}>
                  {h2h.winner}
                </span> wins MVP
              </div>
            </div>
          )}
          
        </>
      )}
      
    </div>
  );
}