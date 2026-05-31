import React from 'react';
import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav style={{
      backgroundColor: '#1a1a2e',
      padding: '16px 24px',
      display: 'flex',
      gap: '24px',
      alignItems: 'center'
    }}>
      <span style={{ color: '#e94560', fontWeight: 'bold', fontSize: '20px' }}>
        🏀 AwardCast
      </span>
      <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Leaderboard</Link>
      <Link to="/compare" style={{ color: 'white', textDecoration: 'none' }}>Compare</Link>
    </nav>
  );
}