// src/pages/HomePage.js
import React from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import './HomePage.css';

function HomePage() {
  const navigate = useNavigate();

  const handleScanningClick = () => {
    navigate('/scanning');
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
          <p>발견된 취약점을 분석하고 평가 보고서를 생성합니다.</p>
          <ul>
            <li>취약점 심각도 평가</li>
            <li>보안 위험 분석</li>
            <li>해결책 제안</li>
            <li>보고서 생성</li>
          </ul>
          <button onClick={() => alert('취약점 분석 기능으로 이동합니다.')}>취약점 분석</button>
        </div>

        <div className="option-card">
          <h3>공격 시뮬레이션</h3>
          <p>발견된 취약점을 기반으로 공격 시뮬레이션을 수행합니다.</p>
          <ul>
            <li>침투 테스트</li>
            <li>권한 상승 테스트</li>
            <li>악성코드 탐지 우회 테스트</li>
            <li>시스템 보안 검증</li>
          </ul>
          <button onClick={() => alert('공격 시뮬레이션 기능으로 이동합니다.')}>공격 시뮬레이션</button>
        </div>
      </div>
    </Layout>
  );
}

export default HomePage;