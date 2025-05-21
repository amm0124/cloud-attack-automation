// src/components/Layout.js
import React from 'react';
import Header from '../header/Header';
import Footer from '../footer/Footer';
import './Layout.css';

function Layout({ children }) {
  return (
    <div className="layout">
      <Header />
      <main className="main-content">
        {children}
      </main>
      <Footer />
    </div>
  );
}

export default Layout;