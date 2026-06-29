import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Leaderboard from './pages/Leaderboard';
import PlayerPage from './pages/PlayerPage';
import Compare from './pages/Compare';
import Snubs from './pages/Snubs';
import DpoySnubs from './pages/DpoySnubs';




function App() {
  return (
    <Router>
      <Navbar />
      <div style={{ padding: '20px' }}>
        <Routes>
          <Route path="/" element={<Leaderboard />} />
          <Route path="/player/:id" element={<PlayerPage />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/snubs" element={<Snubs />} />
          <Route path="/dpoy-snubs" element={<DpoySnubs />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;