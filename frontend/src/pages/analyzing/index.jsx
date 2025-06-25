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
        <p className="page-description">수집한 자격 증명 정보에 과도한 권한이 적용되어 있는지, 최소 권한 원칙이 위배되는지 확인합니다.</p>

        <div className="scanning-options">

          <div className="option-card">
            <h3>AWS IAM 자격 증명 검사</h3>
            <p>AWS IAM 사용자 자격 증명을 검사하여 잠재적 위험을 분석합니다.</p>
            <ul>
              <li>권한 분석</li>
              <li>과도한 권한 식별</li>

            </ul>
            <Link to="/analyzing/aws/iam" className="option-button">시작하기</Link>
          </div>

           <div className="option-card">
            <h3>AWS EC2 자격 증명 검사</h3>
            <p>AWS EC2 인스턴스에 대한 권한 구성을 검사하여 보안 위험을 분석합니다.</p>
            <ul>
              <li>EC2 인스턴스 권한 분석</li>
              <li>과도한 인스턴스 제어 권한 식별</li>
                <li>인바운드 / 아웃바운드 규칙 포함 분석</li>
            </ul>
            <Link to="/analyzing/aws/ec2" className="option-button">시작하기</Link>
          </div>

           <div className="option-card">
            <h3>AWS S3 자격 증명 검사</h3>
            <p>AWS S3 버킷의 접근 권한을 분석하여 잠재적인 데이터 노출 위험을 점검합니다.</p>
            <ul>
              <li>S3 버킷 공개 여부 확인</li>
              <li>과도한 접근 권한 식별</li>
            </ul>
            <Link to="/analyzing/aws/s3" className="option-button">시작하기</Link>
          </div>

           <div className="option-card">
            <h3>AWS Lambda</h3>
            <p>Lambda 함수의 실행 및 연결 권한을 분석하여 보안 설정을 진단합니다.</p>
            <ul>
              <li>Lambda 실행 권한 분석</li>
              <li>외부 서비스와의 과도한 연결 권한 식별</li>
            </ul>
            <Link to="/analyzing/aws/lambda" className="option-button">시작하기</Link>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default AnalyzingIndexPage;