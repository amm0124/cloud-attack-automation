// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ScanningPage from './pages/ScanningPage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/scanning" element={<ScanningPage />} />
        {/* 추후 다른 페이지 추가 */}
        {/* <Route path="/vulnerability" element={<VulnerabilityPage />} /> */}
        {/* <Route path="/attack" element={<AttackPage />} /> */}
      </Routes>
    </Router>
  );
}

export default App;