import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import client from '../api/client';

export default function DpoySnubs() {
  const [snubs, setSnubs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [threshold, setThreshold] = useState(0.85);

  useEffect(() => {
    setLoading(true);
    client.get(`/predictions/dpoy-snubs/${threshold}`)
      .then(res => {
        setSnubs(res.data);
        setLoading(false);
      });
  }, [threshold]);

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <h1 style={{ color: '#e94560' }}>Historical DPOY Snubs</h1>
      <p style={{ color: '#aaa' }}>
        Seasons where the model identified a statistically elite defender but voters chose someone else.
        Reveals positional bias in DPOY voting — guards with elite steal rates are consistently overlooked.
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
              {['Season', 'Player', 'Model Confidence', 'DPOY Rank', 'BPG', 'SPG', 'Def Rating', 'Actual Winner'].map(h => (
                <th key={h} style={{ color: '#aaa', textAlign: 'left', padding: '8px 16px', whiteSpace: 'nowrap' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {snubs.map((row, i) => (
              <tr key={i} style={{ borderBottom: '1px solid #1a1a2e' }}>
                <td style={{ padding: '8px 16px', color: '#aaa' }}>{row.season}</td>
                <td style={{ padding: '8px 16px' }}>
                  <Link to={`/player/${row.player_id}`} style={{ color: '#4a90d9', textDecoration: 'none' }}>
                    {row.full_name}
                  </Link>
                </td>
                <td style={{ padding: '8px 16px', color: '#e94560', fontWeight: 'bold' }}>
                  {(row.dpoy_probability * 100).toFixed(1)}%
                </td>
                <td style={{ padding: '8px 16px', color: '#aaa' }}>
                  {row.dpoy_rank ? `#${row.dpoy_rank}` : 'Not voted'}
                </td>
                <td style={{ padding: '8px 16px', color: 'white' }}>{row.blocks_per_game}</td>
                <td style={{ padding: '8px 16px', color: 'white' }}>{row.steals_per_game}</td>
                <td style={{ padding: '8px 16px', color: 'white' }}>{row.def_rating}</td>
                <td style={{ padding: '8px 16px' }}>
                  {row.actual_winner ? (
                    <Link to={`/player/${row.actual_winner_id}`} style={{ color: '#4a90d9', textDecoration: 'none' }}>
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