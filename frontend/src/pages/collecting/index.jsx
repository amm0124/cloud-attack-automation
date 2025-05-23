// src/pages/index.js
import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/layout/Layout';
import './index.css';

function GithubCollectPage() {
  return (
    <Layout>
      <div className="github-collect-page">
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


        </div>
      </div>
    </Layout>
  );
}

export default GithubCollectPage;