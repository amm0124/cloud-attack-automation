// src/pages/ScanningPage.js
import React from 'react';
import Layout from '../components/layout/Layout';
import './ScanningPage.css';

function ScanningPage() {
  return (
    <Layout>
      <div className="scanning-page">
        <h2>공개 저장소 스캐닝을 통한 자격 증명 수집</h2>
        <p className="page-description">GitHub와 같은 공개 저장소에 노출된 자격 증명 수집</p>

        <div className="scan-form">
          <h3>스캔 대상 설정</h3>

          <div className="form-group">
            <label htmlFor="target">스캔 대상 IP 또는 도메인:</label>
            <input
              type="text"
              id="target"
              placeholder="예: 192.168.1.1 또는 example.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="scan-type">스캔 유형:</label>
            <select id="scan-type">
              <option value="quick">빠른 스캔</option>
              <option value="full">전체 스캔</option>
              <option value="port">포트 스캔</option>
              <option value="vulnerability">취약점 스캔</option>
            </select>
          </div>

          <button onClick={() => alert('스캔을 시작합니다.')}>스캔 시작</button>
        </div>
      </div>
    </Layout>
  );
}

export default ScanningPage;