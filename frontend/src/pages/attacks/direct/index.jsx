// src/pages/index.js
import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../../components/layout/Layout';
import './index.css';

function DirectAttackIndexPage() {
  return (
    <Layout>
      <div className="scanning-menu-page">
        <h2>Direct index page</h2>
        <p className="page-description">Direct Attack</p>

        <div className="scanning-options">

          <div className="option-card">
            <h3>ssh brute force</h3>
            <p>ssh brute force</p>
            <ul>
              <li>SSH brute force</li>
              <li>dd</li>
              <li>dd</li>
              <li>dd</li>
            </ul>
            <Link to="/attacks/direct/ssh-brute-force" className="option-button">이동하기</Link>
          </div>

           <div className="option-card">
            <h3>ssh race condition</h3>
            <p>ssh race condition cve 2024-6387</p>
            <ul>
              <li>Docker</li>
              <li>Jenkins</li>
              <li>dd</li>
              <li>ㅇㅇ</li>
            </ul>
            <Link to="/attacks/direct/ssh-race-condition" className="option-button">이동하기</Link>
          </div>

           <div className="option-card">
            <h3>EC2 임시 키 발급</h3>
            <p>EC2 임시 키 발급</p>
            <ul>
              <li>EC2 임시 키 발급</li>
              <li>ㅇㅇ</li>
              <li>ㅇㅇ</li>
              <li>ㅇㅇ</li>
            </ul>
                <Link to="/attacks/direct/temporary-key" className="option-button">이동하기</Link>
          </div>

            <div className="option-card">
            <h3>EC2 DOS </h3>
            <p>EC2 DOS </p>
            <ul>
              <li>Docker</li>
              <li>Jenkins</li>
              <li>dd</li>
              <li>ㅇㅇ</li>
            </ul>
            <Link to="/attacks/direct/dos" className="option-button">이동하기</Link>
          </div>

            <div className="option-card">
            <h3>LAMBDA 악성 코드 삽입</h3>
            <p>LAMBDA 악성 코드 삽입</p>
            <ul>
              <li>Docker</li>
              <li>Jenkins</li>
              <li>dd</li>
              <li>ㅇㅇ</li>
            </ul>
            <Link to="/attacks/direct/lambda-injection" className="option-button">이동하기</Link>
          </div>


        </div>
      </div>
    </Layout>
  );
}

export default DirectAttackIndexPage;