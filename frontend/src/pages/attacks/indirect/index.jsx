// src/pages/index.js
import React from 'react';
import { Link } from 'react-router-dom';
import Layout from '../../../components/layout/Layout';
import './index.css';

function IndirectAttackIndexPage() {
  return (
    <Layout>
      <div className="scanning-menu-page">
        <h2>Indirect Attack index page</h2>
        <p className="page-description">Attack index page</p>

        <div className="scanning-options">

          <div className="option-card">
            <h3>Docker api attack </h3>
            <p>Docker api attack </p>
            <ul>
              <li>Docker api attack</li>
              <li>dd</li>
              <li>dd</li>
              <li>dd</li>
            </ul>
            <Link to="/attacks/indirect/jenkins" className="option-button">이동하기</Link>
          </div>



        </div>
      </div>
    </Layout>
  );
}

export default IndirectAttackIndexPage;