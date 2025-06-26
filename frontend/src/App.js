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

import AttackIndexPage from "./pages/attacks";





// direct attack - ec2
import DirectAttackIndexPage from "./pages/attacks/direct";

import DirectSshBruteForceAttackPage from "./pages/attacks/direct/ssh/DirectSshBruteForceAttackPage";
import DirectSshRaceConditionAttackPage from "./pages/attacks/direct/ssh/DirectSshRaceConditionAttackPage";
import DirectTemporaryKeyAttackPage from "./pages/attacks/direct/persistence/DirectTemporaryKeyAttackPage";
import Ec2StopAttackPage from "./pages/attacks/direct/ec2/Ec2StopAttackPage";
import Ec2RemoveAttackPage from "./pages/attacks/direct/ec2/Ec2RemoveAttackPage";

/*import DirectDosAttackPage from "./pages/attacks/direct/dos/DirectDosAttackPage";*/

// direct attack - lambda
import DirectLambdaInjectionAttackPage from "./pages/attacks/direct/lambda/DirectLambdaInjectionAttackPage";
import DirectLambdaDownloadAttackPage from "./pages/attacks/direct/lambda/DirectLambdaDownloadAttackPage";
import DirectLambdaRemoveAttackPage from "./pages/attacks/direct/lambda/DirectLambdaRemoveAttackPage";
import DirectLambdaStopAttackPage from "./pages/attacks/direct/lambda/DirectLambdaStopAttackPage";


import IndirectAttackIndexPage from "./pages/attacks/indirect";
import IndirectDockerAttackPage from "./pages/attacks/indirect/docker/IndirectDockerAttackPage";

//import PolicyAttackIndexPage from "./pages/attacks/policy";
//import PolicyMitmAttackPage from "./pages/attacks/policy/mitm/PolicyMitmAttackPage";

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

        <Route path="/attacks" element={<AttackIndexPage />} />

        <Route path="/attacks/direct" element={<DirectAttackIndexPage />} />

        <Route path="/attacks/direct/ssh-brute-force" element={<DirectSshBruteForceAttackPage />} />
        <Route path="/attacks/direct/ssh-race-condition" element={<DirectSshRaceConditionAttackPage />} />
        <Route path="/attacks/direct/temporary-key" element={<DirectTemporaryKeyAttackPage />} />
        {/*<Route path="/attacks/direct/dos" element={<DirectDosAttackPage />} />*/}
        <Route path="/attacks/direct/ec2-stop" element={<Ec2StopAttackPage />} />
        <Route path="/attacks/direct/ec2-remove" element={<Ec2RemoveAttackPage />} />


        <Route path="/attacks/direct/lambda-injection" element={<DirectLambdaInjectionAttackPage />} />
        <Route path="/attacks/direct/download-lambda" element={<DirectLambdaDownloadAttackPage/>} />
        <Route path="/attacks/direct/remove-lambda" element={<DirectLambdaRemoveAttackPage/>} />
        <Route path="/attacks/direct/stop-lambda" element={<DirectLambdaStopAttackPage/>} />

        <Route path="/attacks/indirect" element={<IndirectAttackIndexPage />} />
        <Route path="/attacks/indirect/docker" element={<IndirectDockerAttackPage />} />



        {/*<Route path="/attacks/policy" element={<PolicyAttackIndexPage />} />*/}
        {/*<Route path="/attacks/policy/mitm" element={<PolicyMitmAttackPage />} />*/}





      </Routes>
    </Router>
  );
}

export default App;