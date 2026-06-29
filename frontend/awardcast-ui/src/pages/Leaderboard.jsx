import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Link } from 'react-router-dom';
import client from '../api/client';

const SEASONS = [
  2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016,
  2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005
];

export default function Leaderboard() {
  const [season, setSeason] = useState(2026);
  const [award, setAward] = useState('mvp');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    client.get(`/leaderboard/${award}/${season}`)
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [season, award]);

  const probKey = award === 'mvp' ? 'mvp_probability' : 'dpoy_probability';

  const chartData = data.slice(0, 10).map(p => ({
    name: p.full_name.split(' ').map((n, i, arr) =>
      i === arr.length - 1 ? n : n[0] + '.'
    ).join(' '),
    probability: parseFloat((p[probKey] * 100).toFixed(1)),
    full_name: p.full_name,
    player_id: p.player_id,
  }));

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <h1 style={{ color: '#e94560' }}>
        {award.toUpperCase()} Leaderboard
      </h1>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', alignItems: 'center' }}>
        <select
          value={season}
          onChange={e => setSeason(Number(e.target.value))}
          style={{
            padding: '8px 16px',
            fontSize: '16px',
            backgroundColor: '#1a1a2e',
            color: 'white',
            border: '1px solid #e94560',
            borderRadius: '4px'
          }}
        >
          {SEASONS.map(s => (
            <option key={s} value={s}>{s - 1}-{String(s).slice(2)}</option>
          ))}
        </select>

        {['mvp', 'dpoy'].map(a => (
          <button
            key={a}
            onClick={() => setAward(a)}
            style={{
              padding: '8px 20px',
              backgroundColor: award === a ? '#e94560' : '#1a1a2e',
              color: 'white',
              border: '1px solid #e94560',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: award === a ? 'bold' : 'normal',
              textTransform: 'uppercase',
              fontSize: '14px'
            }}
          >
            {a}
          </button>
        ))}
      </div>

      {loading && <p style={{ color: 'white' }}>Loading...</p>}

      {!loading && chartData.length > 0 && (
        <>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} layout="vertical">
              <XAxis type="number" domain={[0, 100]} tickFormatter={v => `${v}%`} stroke="white" />
              <YAxis type="category" dataKey="name" stroke="white" width={150} />
              <Tooltip formatter={v => `${v}%`} />
              <Bar dataKey="probability" radius={[0, 4, 4, 0]}>
                {chartData.map((_, i) => (
                  <Cell key={i} fill={i === 0 ? '#e94560' : '#4a90d9'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '24px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #333' }}>
                <th style={{ color: '#aaa', textAlign: 'left', padding: '8px' }}>Rank</th>
                <th style={{ color: '#aaa', textAlign: 'left', padding: '8px' }}>Player</th>
                <th style={{ color: '#aaa', textAlign: 'right', padding: '8px' }}>
                  {award.toUpperCase()} Probability
                </th>
              </tr>
            </thead>
            <tbody>
              {data.map((player, i) => (
                <tr key={player.player_id} style={{ borderBottom: '1px solid #1a1a2e' }}>
                  <td style={{ color: '#aaa', padding: '8px' }}>#{i + 1}</td>
                  <td style={{ padding: '8px' }}>
                    <Link
                      to={`/player/${player.player_id}`}
                      style={{ color: 'white', textDecoration: 'none' }}
                    >
                      {player.full_name}
                    </Link>
                  </td>
                  <td style={{ color: '#e94560', textAlign: 'right', padding: '8px', fontWeight: 'bold' }}>
                    {(player[probKey] * 100).toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}