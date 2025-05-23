// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import GitHubCollectPage from './pages/collecting/github/GitHubCollectPage';
import CollectingIndexPage from './pages/collecting';
import AnalyzingIndexPage from './pages/analyzing';
import IamAnalyzingPage from "./pages/analyzing/iam/IamAnalyzePage";
import Ec2AnalyzingPage from "./pages/analyzing/ec2/Ec2AnalyzePage";
import S3AnalyzingPage from "./pages/analyzing/s3/S3AnalyzePage";
import LambdaAnalyzingPage from "./pages/analyzing/lambda/LambdaAnalyzePage";

import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/collecting" element={<CollectingIndexPage />} />
        <Route path="/collecting/github" element={<GitHubCollectPage />} />
        <Route path="/analyzing" element={<AnalyzingIndexPage />} />
        <Route path="/analyzing/aws/iam" element={<IamAnalyzingPage />} />
        <Route path="/analyzing/aws/ec2" element={<Ec2AnalyzingPage />} />
        <Route path="/analyzing/aws/s3" element={<S3AnalyzingPage />} />
        <Route path="/analyzing/aws/lambda" element={<LambdaAnalyzingPage />} />



      </Routes>
    </Router>
  );
}

export default App;