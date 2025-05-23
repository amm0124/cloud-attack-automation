// src/pages/index.js
import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../../components/layout/Layout';
import './index.css';

function PolicyAttackIndexPage() {
  return (
    <Layout>
      <div className="scanning-menu-page">
        <h2>Policy index page</h2>
        <p className="page-description">Attack index page</p>

        <div className="scanning-options">

          <div className="option-card">
            <h3>organization을 통한 mitm </h3>
            <p>organization을 통한 mitm </p>
            <ul>
              <li>organization을 통한 mitm</li>
              <li>dd</li>
              <li>dd</li>
              <li>dd</li>
            </ul>
            <Link to="/attacks/policy/mitm" className="option-button">이동하기</Link>
          </div>

        </div>
      </div>
    </Layout>
  );
}

export default PolicyAttackIndexPage;