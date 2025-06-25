// src/pages/index.js
import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../../components/layout/Layout';
import './index.css';

function IndirectAttackIndexPage() {
  return (
    <Layout>
      <div className="scanning-menu-page">
        <h2>애플리케이션 취약점을 통한 간접적 클라우드 서비스 침투</h2>
        <p className="page-description">애플리케이션 취약점을 통해 간접적으로 클라우드 서비스를 공격합니다.</p>

        <div className="scanning-options">



          <div className="option-card">
            <h3>Docker Container Escape Attack</h3>
            <p>공격 대상 : EC2</p>
            <ul>
              <li>컨테이너 관리 서비스 Docker Deamon을 악용하여 호스트 시스템까지 접근</li>
              <li>Docker Deamon에 접근 가능한 Docker API 2375번 포트를 통한 침투</li>
            </ul>
            <Link to="/attacks/indirect/docker" className="option-button">이동하기</Link>
          </div>



        </div>
      </div>
    </Layout>
  );
}

export default IndirectAttackIndexPage;