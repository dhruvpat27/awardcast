import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, ReferenceLine
} from 'recharts';
import client from '../api/client';

export default function PlayerPage() {
  const { id } = useParams();
  const [stats, setStats] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [playerName, setPlayerName] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    client.get(`/players/${id}`).then(res => {
      setStats(res.data);
      if (res.data.length > 0) setPlayerName(res.data[0].full_name);
    });

    // Fetch MVP probability for each season
    client.get(`/predictions/player/${id}`).then(res => {
      setPredictions(res.data);
      setLoading(false);
    });
  }, [id]);

  const chartData = predictions.map(p => ({
    season: p.season,
    probability: parseFloat((p.mvp_probability * 100).toFixed(1)),
    won: p.mvp_winner,
    rank: p.mvp_rank,
  }));

  const CustomDot = (props) => {
    const { cx, cy, payload } = props;
    if (payload.won) {
      return <circle cx={cx} cy={cy} r={8} fill="#e94560" stroke="white" strokeWidth={2} />;
    }
    return <circle cx={cx} cy={cy} r={4} fill="#4a90d9" />;
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      {loading ? (
        <p style={{ color: 'white' }}>Loading...</p>
      ) : (
        <>
          <h1 style={{ color: '#e94560' }}>{playerName}</h1>

          {chartData.length > 0 && (
            <>
              <h2 style={{ color: '#aaa', fontSize: '16px', fontWeight: 'normal' }}>
                MVP Probability by Season
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="season" stroke="white" tick={{ fontSize: 11 }} />
                  <YAxis stroke="white" tickFormatter={v => `${v}%`} domain={[0, 100]} />
                  <Tooltip formatter={v => `${v}%`} />
                  <ReferenceLine y={50} stroke="#555" strokeDasharray="4 4" />
                  <Line
                    type="monotone"
                    dataKey="probability"
                    stroke="#4a90d9"
                    strokeWidth={2}
                    dot={<CustomDot />}
                  />
                </LineChart>
              </ResponsiveContainer>
              <p style={{ color: '#aaa', fontSize: '12px' }}>
                🔴 Red dot = MVP winner that season
              </p>
            </>
          )}

          <h2 style={{ color: '#aaa', fontSize: '16px', fontWeight: 'normal', marginTop: '32px' }}>
            Career Stats
          </h2>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #333' }}>
                {['Season', 'PPG', 'APG', 'RPG', 'GP', 'MVP Rank'].map(h => (
                  <th key={h} style={{ color: '#aaa', textAlign: 'left', padding: '8px' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {stats.map((row, i) => {
                const pred = predictions.find(p => p.season === row.season);
                return (
                  <tr key={i} style={{
                    borderBottom: '1px solid #1a1a2e',
                    backgroundColor: pred?.mvp_winner ? 'rgba(233,69,96,0.1)' : 'transparent'
                  }}>
                    <td style={{ padding: '8px', color: pred?.mvp_winner ? '#e94560' : 'white' }}>
                      {row.season} {pred?.mvp_winner && '🏆'}
                    </td>
                    <td style={{ padding: '8px', color: 'white' }}>{row.points_per_game}</td>
                    <td style={{ padding: '8px', color: 'white' }}>{row.assists_per_game}</td>
                    <td style={{ padding: '8px', color: 'white' }}>{row.rebounds_per_game}</td>
                    <td style={{ padding: '8px', color: 'white' }}>{row.games_played}</td>
                    <td style={{ padding: '8px', color: '#aaa' }}>
                      {pred?.mvp_rank ? `#${pred.mvp_rank}` : '-'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}