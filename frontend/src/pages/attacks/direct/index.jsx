// src/pages/index.js
import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../../components/layout/Layout';
import './index.css';

function DirectAttackIndexPage() {
  return (
    <Layout>
      <div className="scanning-menu-page">
        <h2>클라우드 플랫폼 서비스 직접 공격</h2>
        <p className="page-description">클라우드 플랫폼 서비스 대상 공격을 시뮬레이션합니다.</p>

        <div className="scanning-options">

          <div className="option-card">
            <h3>[EC2] - SSH brute force</h3>
            <p>공격 대상 : EC2</p>
            <ul>
              <li>EC2를 대상으로 SSH Brute force 공격 수행</li>
            </ul>
            <Link to="/attacks/direct/ssh-brute-force" className="option-button">이동하기</Link>
          </div>

           <div className="option-card">
            <h3>[EC2] - SSH Race Condition 공격</h3>
            <p>공격 대상 : EC2</p>
            <ul>
               <li>EC2를 대상으로 CVE 2024-6387 공격 수행</li>
                <li>취약 OpenSSH 버전 : 8.5p1이상 9.8p1미만</li>
            </ul>
            <Link to="/attacks/direct/ssh-race-condition" className="option-button">이동하기</Link>
          </div>

           <div className="option-card">
            <h3>[EC2] - EC2 임시 키 발급</h3>
            <p>공격 대상 : EC2</p>
            <ul>
              <li>새로운 EC2 키 발급을 통한 지속적 공격 확보</li>
            </ul>
                <Link to="/attacks/direct/temporary-key" className="option-button">이동하기</Link>
          </div>

          {/*  <div className="option-card">*/}
          {/*  <h3>[EC2] - EC2 DoS</h3>*/}
          {/*  <p>공격 대상 : EC2</p>*/}
          {/*  <ul>*/}
          {/*    <li>EC2를 대상으로 DoS(Denial of Service) 공격 수행</li>*/}
          {/*  </ul>*/}
          {/*  <Link to="/attacks/direct/dos" className="option-button">이동하기</Link>*/}
          {/*</div>*/}

            <div className="option-card">
                <h3>[EC2] - EC2 중지</h3>
                <p>공격 대상 : EC2</p>
                <ul>
                    <li>EC2 서비스 완전 중지</li>
                </ul>
                <Link to="/attacks/direct/ec2-stop" className="option-button">이동하기</Link>
            </div>

            <div className="option-card">
                <h3>[EC2] - EC2 삭제</h3>
                <p>공격 대상 : EC2</p>
                <ul>
                    <li>EC2 서비스 완전 삭제</li>
                </ul>
                <Link to="/attacks/direct/ec2-remove" className="option-button">이동하기</Link>
            </div>

            <div className="option-card">
                <h3>[Lambda] - Lambda 코드 다운로드</h3>
                <p>공격 대상 : Lambda</p>
                <ul>
                    <li>AWS Lambda에 올라온 코드 다운로드</li>
                </ul>
                <Link to="/attacks/direct/download-lambda" className="option-button">이동하기</Link>
            </div>


            <div className="option-card">
            <h3>[Lambda] - Lambda 악성 코드 삽입</h3>
            <p>공격 대상 : Lambda</p>
            <ul>
              <li>AWS Lambda 대상으로 악성 코드 삽입</li>
            </ul>
            <Link to="/attacks/direct/lambda-injection" className="option-button">이동하기</Link>
          </div>


            <div className="option-card">
                <h3>[Lambda] - Lambda 삭제</h3>
                <p>공격 대상 : Lambda</p>
                <ul>
                    <li>AWS Lambda 삭제</li>
                </ul>
                <Link to="/attacks/direct/remove-lambda" className="option-button">이동하기</Link>
            </div>





        </div>
      </div>
    </Layout>
  );
}

export default DirectAttackIndexPage;