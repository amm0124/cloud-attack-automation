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
    navigate('/attack');
  };


  return (
    <Layout>
      <h2>주요 기능 선택</h2>

      <div className="main-options">
        <div className="option-card">
          <h3>스캐닝</h3>
          <p>클라우드 환경에 대한 자동화된 보안 스캔을 실행합니다.</p>
          <ul>
            <li>네트워크 스캔</li>
            <li>포트 스캔</li>
            <li>서비스 탐지</li>
            <li>취약점 자동 스캔</li>
          </ul>
          <button onClick={handleScanningClick}>스캐닝 시작</button>
        </div>

        <div className="option-card">
          <h3>취약점 분석</h3>
          <p>수집한 자격 증명 정보를 통해 접근 가능한 AWS 서비스 분석</p>
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
            <li>ㅇㅇ</li>
            <li>ㅇㅇ</li>
            <li>ㅇㅇ</li>
            <li>ㅇㅇ</li>
          </ul>

          <button onClick={handleAttackClick}>공격 시뮬레이션 시작</button>
        </div>
      </div>
    </Layout>
  );
}

export default HomePage;