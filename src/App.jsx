import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import PreSubmissionGuide from './components/PreSubmissionGuide';
import UploadView from './components/UploadView';
import ComplianceDashboard from './components/ComplianceDashboard';
import EvidenceInspector from './components/EvidenceInspector';
import AuditReportView from './components/AuditReportView';
import LoginPage from './components/LoginPage';
import api from './services/api';
import { MOCK_VENDORS } from './data/mockVendors';
import './App.css';

export default function App() {
  // Authentication state: user object or null
  const [currentUser, setCurrentUser] = useState(null);

  // Navigation tabs: 'guide' | 'upload' | 'dashboard' | 'inspector' | 'export'
  const [activeTab, setActiveTab] = useState('guide');
  
  // Currently active audited vendor
  const [selectedVendor, setSelectedVendor] = useState(MOCK_VENDORS[0]);
  
  // Currently inspected document in the Evidence Inspector
  const [activeDocId, setActiveDocId] = useState('doc-gst');

  // Scanning animation states
  const [isScanning, setIsScanning] = useState(false);
  const [scanStage, setScanStage] = useState(1);

  // Loading skeleton and error states
  const [isLoadingVendor, setIsLoadingVendor] = useState(false);
  const [globalError, setGlobalError] = useState(null);

  // Fetch initial vendor data on mount from FastAPI backend (or fallback)
  useEffect(() => {
    let isMounted = true;
    async function loadInitialVendor() {
      setIsLoadingVendor(true);
      try {
        const freshVendor = await api.getVendorDossier('vendor-1');
        if (isMounted && freshVendor) {
          setSelectedVendor(freshVendor);
          if (freshVendor.documents && freshVendor.documents.length > 0) {
            setActiveDocId(freshVendor.documents[0].id);
          }
        }
      } catch (err) {
        console.warn('Initial vendor load used fallback benchmark:', err);
      } finally {
        if (isMounted) setIsLoadingVendor(false);
      }
    }
    loadInitialVendor();
    return () => { isMounted = false; };
  }, []);

  const handleLogin = (userData) => {
    setCurrentUser(userData);
  };

  const handleGuestLogin = (guestData) => {
    setCurrentUser(guestData);
  };

  const handleLogout = () => {
    setCurrentUser(null);
  };

  const handleVendorSelected = (vendor) => {
    setSelectedVendor(vendor);
    if (vendor && vendor.documents && vendor.documents.length > 0) {
      setActiveDocId(vendor.documents[0].id);
    }
    setActiveTab('dashboard');
  };

  const handleInspectDocument = (docId) => {
    if (docId) setActiveDocId(docId);
    setActiveTab('inspector');
  };

  const handleViewReport = () => {
    setActiveTab('export');
  };

  const handleProceedToUpload = () => {
    setActiveTab('upload');
  };

  // If not logged in, show the dedicated login screen with guest login option
  if (!currentUser) {
    return (
      <LoginPage 
        onLogin={handleLogin}
        onGuestLogin={handleGuestLogin}
      />
    );
  }

  return (
    <div className="tenderguard-app-shell">
      {/* Top Navigation & Context */}
      <Header 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        selectedVendor={selectedVendor}
        onResetToUpload={() => setActiveTab('upload')}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      {/* Global Error Banner if API error occurs */}
      {globalError && (
        <div className="global-error-strip">
          <span>⚠️ {globalError}</span>
          <button onClick={() => setGlobalError(null)}>Dismiss</button>
        </div>
      )}

      {/* Main Content Area */}
      <main className="app-main-content">
        {isLoadingVendor ? (
          <div className="loading-skeleton-container">
            <div className="skeleton-hero-card"></div>
            <div className="skeleton-grid">
              <div className="skeleton-card"></div>
              <div className="skeleton-card"></div>
            </div>
          </div>
        ) : (
          <>
            {activeTab === 'guide' && (
              <PreSubmissionGuide 
                onProceedToUpload={handleProceedToUpload}
              />
            )}

            {activeTab === 'upload' && (
              <UploadView 
                onVendorSelected={handleVendorSelected}
                selectedVendor={selectedVendor}
                isScanning={isScanning}
                setIsScanning={setIsScanning}
                scanStage={scanStage}
                setScanStage={setScanStage}
              />
            )}

            {activeTab === 'dashboard' && (
              <ComplianceDashboard 
                vendor={selectedVendor}
                onInspectDocument={handleInspectDocument}
                onViewReport={handleViewReport}
                onChangeVendor={() => setActiveTab('upload')}
              />
            )}

            {activeTab === 'inspector' && (
              <EvidenceInspector 
                vendor={selectedVendor}
                activeDocId={activeDocId}
                setActiveDocId={setActiveDocId}
                onBackToDashboard={() => setActiveTab('dashboard')}
              />
            )}

            {activeTab === 'export' && (
              <AuditReportView 
                vendor={selectedVendor}
                onBack={() => setActiveTab('dashboard')}
              />
            )}
          </>
        )}
      </main>

      {/* Minimal Footer */}
      <footer className="app-footer-bar no-print">
        <div className="footer-content">
          <div className="f-left">
            <span className="dot-live"></span>
            <span>TenderGuard AI 4.0 · Real-time OCR & Vision-Language Verification Engine</span>
          </div>
          <div className="f-right">
            <span>Compliant with GFR 2017 & GeM Procurement Manual</span>
            <span className="pipe">|</span>
            <span>Zero-Retention Certified</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
