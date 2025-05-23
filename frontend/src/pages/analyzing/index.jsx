// src/pages/index.js
import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../components/layout/Layout';
import './index.css';

function AnalyzingIndexPage() {
  return (
    <Layout>
      <div className="scanning-menu-page">
        <h2>수집한 자격 증명 정보를 통한 취약점 분석</h2>
        <p className="page-description">수집한 자격 증명 정보로 접근 가능한 AWS(Amazon Web Service) 주요 서비스 취약점 분석</p>

        <div className="scanning-options">

          <div className="option-card">
            <h3>AWS IAM 자격 증명 검사</h3>
            <p>AWS IAM 사용자 자격 증명을 검사하여 잠재적 위험을 분석합니다.</p>
            <ul>
              <li>권한 분석</li>
              <li>비활성 키 탐지</li>
              <li>과도한 권한 식별</li>
              <li>보안 위반 사항 검출</li>
            </ul>
            <Link to="/analyzing/aws/iam" className="option-button">시작하기</Link>
          </div>

           <div className="option-card">
            <h3>AWS EC2 자격 증명 검사</h3>
            <p>AWS EC2 분석</p>
            <ul>
              <li>보안 그룹</li>
              <li>포트</li>
              <li>접근 가능한 메타데이터</li>
              <li>ㅇㅇ</li>
            </ul>
            <Link to="/analyzing/aws/ec2" className="option-button">시작하기</Link>
          </div>

           <div className="option-card">
            <h3>AWS S3 자격 증명 검사</h3>
            <p>S3 분석</p>
            <ul>
              <li>공개 범위</li>
              <li>정책 분석</li>
              <li>ㅇㅇ</li>
              <li>ㅇㅇ</li>
            </ul>
            <Link to="/analyzing/aws/s3" className="option-button">시작하기</Link>
          </div>

           <div className="option-card">
            <h3>AWS Lambda</h3>
            <p>AWS Lambda 분석</p>
            <ul>
              <li>lambda</li>
              <li>언어 분석</li>
              <li>취약한 라이브러리 탐색</li>
              <li>암호화 시, KMS를 통한 복호화</li>
            </ul>
            <Link to="/analyzing/aws/lambda" className="option-button">시작하기</Link>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default AnalyzingIndexPage;