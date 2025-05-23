// src/pages/index.js
import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/layout/Layout';
import './index.css';

function AttackIndexPage() {
  return (
    <Layout>
      <div className="scanning-menu-page">
        <h2>Attack index page</h2>
        <p className="page-description">Attack index page</p>

        <div className="scanning-options">

          <div className="option-card">
            <h3>클라우드 플랫폼 서비스 직접 공격 </h3>
            <p>클라우드 플랫폼 서비스 직접 공격 </p>
            <ul>
              <li>SSH brute force</li>
              <li>dd</li>
              <li>dd</li>
              <li>dd</li>
            </ul>
            <Link to="/attacks/direct" className="option-button">이동하기</Link>
          </div>

           <div className="option-card">
            <h3>애플리케이션 취약점을 통한 간접적 클라우드 서비스 침투 </h3>
            <p>애플리케이션 취약점을 통한 간접적 클라우드 서비스 침투 </p>
            <ul>
              <li>Docker</li>
              <li>Jenkins</li>
              <li>dd</li>
              <li>ㅇㅇ</li>
            </ul>
            <Link to="/attacks/indirect" className="option-button">이동하기</Link>
          </div>

           <div className="option-card">
            <h3>정책 기반 비인가 행위 수행 </h3>
            <p>정책 기반 비인가 행위 수행 </p>
            <ul>
              <li>AWS 서브넷 악용</li>
              <li>ㅇㅇ</li>
              <li>ㅇㅇ</li>
              <li>ㅇㅇ</li>
            </ul>
                <Link to="/attacks/policy" className="option-button">이동하기</Link>
          </div>


        </div>
      </div>
    </Layout>
  );
}

export default AttackIndexPage;