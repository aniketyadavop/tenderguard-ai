import React, { useState } from 'react';
import Header from './components/Header';
import PreSubmissionGuide from './components/PreSubmissionGuide';
import UploadView from './components/UploadView';
import ComplianceDashboard from './components/ComplianceDashboard';
import EvidenceInspector from './components/EvidenceInspector';
import AuditReportView from './components/AuditReportView';
import { MOCK_VENDORS } from './data/mockVendors';
import './App.css';

export default function App() {
  // Navigation tabs: 'guide' | 'upload' | 'dashboard' | 'inspector' | 'export'
  const [activeTab, setActiveTab] = useState('guide');
  
  // Currently active audited vendor (defaults to TechNova for instant preview)
  const [selectedVendor, setSelectedVendor] = useState(MOCK_VENDORS[0]);
  
  // Currently inspected document in the Evidence Inspector
  const [activeDocId, setActiveDocId] = useState('doc-gst');

  // Scanning animation states
  const [isScanning, setIsScanning] = useState(false);
  const [scanStage, setScanStage] = useState(1);

  const handleVendorSelected = (vendor) => {
    setSelectedVendor(vendor);
    setActiveDocId(vendor.documents[0].id);
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

  return (
    <div className="tenderguard-app-shell">
      {/* Top Navigation & Context */}
      <Header 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        selectedVendor={selectedVendor}
        onResetToUpload={() => setActiveTab('upload')}
      />

      {/* Main Content Area Based on Active Category */}
      <main className="app-main-content">
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
      </main>

      {/* Mode-style clean minimal footer */}
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
