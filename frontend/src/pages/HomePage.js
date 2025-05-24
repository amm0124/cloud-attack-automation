// src/pages/HomePage.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import './HomePage.css';

function HomePage() {
  const navigate = useNavigate();

  const handleScanningClick = () => {
    navigate('/collecting');
  };

  const handleAnalyzingClick = () => {
    navigate('/analyzing');
  };

  const handleAttackClick = () => {
    navigate('/attacks');
  };

  return (
    <Layout>
      <h2>주요 기능 선택</h2>

      <div className="main-options">
        <div className="option-card">
          <h3>1. 자격 증명 정보 수집</h3>
          <p>공개 저장소에 노출된 자격 증명 정보를 수집할 수 있습니다.</p>
          <ul>
            <li>GitHub</li>
          </ul>
          <button onClick={handleScanningClick}>자격 증명 정보 수집 시작</button>
        </div>

        <div className="option-card">
          <h3>취약점 분석</h3>
          <p>수집한 자격 증명 정보를 통해 접근 가능한 AWS 서비스를 분석합니다.</p>
          <ul>
            <li>IAM</li>
            <li>EC2</li>
            <li>S3</li>
            <li>Lambda</li>
          </ul>
          <button onClick={handleAnalyzingClick}>취약점 분석 시작</button>
        </div>

        <div className="option-card">
          <h3>공격 시뮬레이션</h3>
          <p>발견된 취약점을 기반으로 공격 시뮬레이션을 수행합니다.</p>
          <ul>
            <li>클라우드 인프라스트럭처 대상 공격</li>
            <li>취약한 애플리케이션을 통한 인프라스트럭처 공격</li>
            <li>보안 정책 우회를 통한 공격</li>
          </ul>
          <button onClick={handleAttackClick}>공격 시뮬레이션 시작</button>
        </div>
      </div>
    </Layout>
  );
}

export default HomePage;