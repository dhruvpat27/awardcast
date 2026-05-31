import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import client from '../api/client';

export default function Snubs() {
  const [snubs, setSnubs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [threshold, setThreshold] = useState(0.85);

  useEffect(() => {
    setLoading(true);
    client.get(`/predictions/snubs/${threshold}`)
      .then(res => {
        setSnubs(res.data);
        setLoading(false);
      });
  }, [threshold]);

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <h1 style={{ color: '#e94560' }}>Historical MVP Snubs</h1>
      <p style={{ color: '#aaa' }}>
        Seasons where the model strongly predicted a player to win MVP but voters disagreed.
        This reveals potential voter bias in NBA award history.
      </p>

      <div style={{ marginBottom: '24px' }}>
        <label style={{ color: '#aaa', marginRight: '12px' }}>
          Minimum model confidence:
        </label>
        <select
          value={threshold}
          onChange={e => setThreshold(parseFloat(e.target.value))}
          style={{
            padding: '8px 16px',
            backgroundColor: '#1a1a2e',
            color: 'white',
            border: '1px solid #e94560',
            borderRadius: '4px'
          }}
        >
          <option value={0.95}>95%+</option>
          <option value={0.85}>85%+</option>
          <option value={0.75}>75%+</option>
          <option value={0.65}>65%+</option>
        </select>
        <span style={{ color: '#aaa', marginLeft: '12px' }}>
          {snubs.length} snubs found
        </span>
      </div>

      {loading && <p style={{ color: 'white' }}>Loading...</p>}

      {!loading && (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #333' }}>
              {['Season', 'Player', 'Model Confidence', 'Actual MVP Rank', 'PPG', 'Team Win%', 'Actual Winner'].map(h => (
                <th key={h} style={{ color: '#aaa', textAlign: 'left', padding: '8px', whiteSpace: 'nowrap' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {snubs.map((row, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #1a1a2e' }}>
                <td style={{ padding: '8px', color: '#aaa' }}>{row.season}</td>
                <td style={{ padding: '8px' }}>
                  <Link to={`/player/${row.player_id}`} style={{ color: '#4a90d9', textDecoration: 'none' }}>
                    {row.full_name}
                  </Link>
                </td>
                <td style={{ padding: '8px', color: '#e94560', fontWeight: 'bold' }}>
                  {(row.mvp_probability * 100).toFixed(1)}%
                </td>
                <td style={{ padding: '8px', color: '#aaa' }}>
                  {row.mvp_rank ? `#${row.mvp_rank}` : 'Not voted'}
                </td>
                <td style={{ padding: '8px', color: 'white' }}>{row.points_per_game}</td>
                <td style={{ padding: '8px', color: 'white' }}>
                  {row.team_win_pct ? (row.team_win_pct * 100).toFixed(1) + '%' : '-'}
                </td>
                <td style={{ padding: '8px' }}>
                  {row.actual_winner ? (
                    <Link
                      to={`/player/${row.actual_winner_id}`}
                      style={{ color: '#4a90d9', textDecoration: 'none' }}
                    >
                      {row.actual_winner}
                    </Link>
                  ) : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}