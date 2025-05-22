// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import GitHubCollectPage from './pages/collecting/github/GitHubCollectPage';
import CollectingIndexPage from './pages/collecting';

import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/collecting" element={<CollectingIndexPage />} />
        <Route path="/collecting/github" element={<GitHubCollectPage />} />
        {/* GitHub 스캔 페이지 */}

        {/* 추후 다른 페이지 추가 */}
        {/* <Route path="/vulnerability" element={<VulnerabilityPage />} /> */}
        {/* <Route path="/attack" element={<AttackPage />} /> */}
      </Routes>
    </Router>
  );
}

export default App;