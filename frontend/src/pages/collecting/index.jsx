// src/pages/index.js
import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/layout/Layout';
import './index.css';

function ScanningMenuPage() {
  return (
    <Layout>
      <div className="scanning-menu-page">
        <h2>자격 증명 수집 도구 선택</h2>
        <p className="page-description">다양한 자격 증명 수집 방법 중 하나를 선택하세요</p>

        <div className="scanning-options">
          <div className="option-card">
            <h3>GitHub 저장소 스캔</h3>
            <p>GitHub와 같은 공개 저장소에 노출된 자격 증명을 수집합니다.</p>
            <ul>
              <li>액세스 키 검출</li>
              <li>API 키 및 토큰 검출</li>
              <li>데이터베이스 자격 증명 검출</li>
              <li>하드코딩된 비밀번호 검출</li>
            </ul>
            <Link to="/collecting/github" className="option-button">시작하기</Link>
          </div>

          <div className="option-card">
            <h3>AWS IAM 자격 증명 검사</h3>
            <p>AWS IAM 사용자 자격 증명을 검사하여 잠재적 위험을 분석합니다.</p>
            <ul>
              <li>권한 분석</li>
              <li>비활성 키 탐지</li>
              <li>과도한 권한 식별</li>
              <li>보안 위반 사항 검출</li>
            </ul>
            <Link to="/collection/aws" className="option-button">시작하기</Link>
          </div>

          <div className="option-card">
            <h3>도메인/IP 스캔</h3>
            <p>특정 도메인이나 IP 범위에서 노출된 자격 증명을 스캔합니다.</p>
            <ul>
              <li>URL 매개변수 분석</li>
              <li>공개 API 엔드포인트 검사</li>
              <li>오픈 포트 스캔</li>
              <li>인증서 정보 수집</li>
            </ul>
            <Link to="/collection/domain" className="option-button">시작하기</Link>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default ScanningMenuPage;