import React, { useState, useRef } from 'react';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Sparkles, 
  ArrowRight,
  ShieldCheck,
  Cpu,
  Layers,
  FileCheck,
  RefreshCw
} from 'lucide-react';
import { MOCK_VENDORS } from '../data/mockVendors';

export default function UploadView({ 
  onVendorSelected, 
  selectedVendor, 
  isScanning, 
  setIsScanning,
  scanStage,
  setScanStage
}) {
  const [dragActive, setDragActive] = useState(false);
  const [customFiles, setCustomFiles] = useState([]);
  const fileInputRef = useRef(null);

  const startScanningSimulation = (vendor) => {
    setIsScanning(true);
    setScanStage(1);

    setTimeout(() => setScanStage(2), 700);
    setTimeout(() => setScanStage(3), 1400);
    setTimeout(() => setScanStage(4), 2100);
    setTimeout(() => {
      setIsScanning(false);
      onVendorSelected(vendor);
    }, 2800);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files) => {
    const fileList = Array.from(files).map((f) => ({
      name: f.name,
      size: (f.size / (1024 * 1024)).toFixed(2) + " MB",
      type: f.type || "PDF Document"
    }));
    setCustomFiles(fileList);
    // Trigger scan using default compliant vendor template as base
    startScanningSimulation(MOCK_VENDORS[0]);
  };

  return (
    <div className="upload-view-container">
      {/* Scanning Overlay Animation */}
      {isScanning && (
        <div className="scanning-overlay-modal">
          <div className="scanning-card">
            <div className="scanning-radar-pulse">
              <Cpu size={36} className="radar-icon" />
              <div className="radar-ring r1"></div>
              <div className="radar-ring r2"></div>
            </div>

            <h3 className="scan-title">TenderGuard AI Engine In Progress</h3>
            <p className="scan-desc">
              Cross-referencing extracted OCR tokens against GeM Tender Ref: <strong>GeM/2026/B/89412</strong>
            </p>

            <div className="scan-stepper">
              <div className={`scan-step ${scanStage >= 1 ? 'step-done' : ''} ${scanStage === 1 ? 'step-active' : ''}`}>
                <div className="step-icon">
                  {scanStage > 1 ? <CheckCircle2 size={16} /> : <span className="s-num">1</span>}
                </div>
                <div className="step-txt">
                  <span className="s-title">Dual OCR Spatial Extraction</span>
                  <span className="s-desc">Mapping 2D coordinate bounding boxes on raw filings</span>
                </div>
              </div>

              <div className={`scan-step ${scanStage >= 2 ? 'step-done' : ''} ${scanStage === 2 ? 'step-active' : ''}`}>
                <div className="step-icon">
                  {scanStage > 2 ? <CheckCircle2 size={16} /> : <span className="s-num">2</span>}
                </div>
                <div className="step-txt">
                  <span className="s-title">Vision-Language Entity Parsing</span>
                  <span className="s-desc">Extracting GSTIN, PAN numbers, validity dates, & signatures</span>
                </div>
              </div>

              <div className={`scan-step ${scanStage >= 3 ? 'step-done' : ''} ${scanStage === 3 ? 'step-active' : ''}`}>
                <div className="step-icon">
                  {scanStage > 3 ? <CheckCircle2 size={16} /> : <span className="s-num">3</span>}
                </div>
                <div className="step-txt">
                  <span className="s-title">Cross-Document Reconciliation</span>
                  <span className="s-desc">Checking PAN across GST certificate and PAN card</span>
                </div>
              </div>

              <div className={`scan-step ${scanStage >= 4 ? 'step-done' : ''} ${scanStage === 4 ? 'step-active' : ''}`}>
                <div className="step-icon">
                  {scanStage === 4 ? <RefreshCw size={16} className="spin-icon" /> : <span className="s-num">4</span>}
                </div>
                <div className="step-txt">
                  <span className="s-title">Explainability Tree & Evidence Generation</span>
                  <span className="s-desc">Creating plain English justification & visual proof crops</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Upload Header */}
      <div className="section-header">
        <div className="header-badge-chip">
          <Layers size={14} />
          <span>Stage 2 · Document Intake</span>
        </div>
        <h1 className="section-title">Upload Documents or Test Sample Filings</h1>
        <p className="section-subtitle">
          TenderGuard AI automatically parses GST, PAN, Udyam, and OEM documents, checks validity, and highlights exact visual proof on the source page.
        </p>
      </div>

      <div className="upload-grid-layout">
        {/* Left Column: Drag & Drop Zone */}
        <div className="upload-left-col">
          <div 
            className={`dropzone-box ${dragActive ? 'dropzone-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              ref={fileInputRef}
              type="file" 
              multiple 
              accept=".pdf,.png,.jpg,.jpeg" 
              style={{ display: 'none' }}
              onChange={handleFileInput}
            />

            <div className="dropzone-icon-circle">
              <UploadCloud size={32} />
            </div>

            <h3 className="dropzone-title">Click to upload or drag & drop files here</h3>
            <p className="dropzone-desc">
              Upload GST, PAN, MSME, or OEM Authorization letters. Supports multi-page PDF, PNG, JPG (up to 25MB each).
            </p>

            <div className="dropzone-formats">
              <span className="fmt-pill">PDF (Searchable / Scanned)</span>
              <span className="fmt-pill">PNG / JPEG (200+ DPI)</span>
              <span className="fmt-pill">Multi-file Batch</span>
            </div>
          </div>

          {customFiles.length > 0 && (
            <div className="uploaded-files-list">
              <h4>Queued Files for Analysis ({customFiles.length}):</h4>
              {customFiles.map((f, i) => (
                <div key={i} className="queued-file-item">
                  <FileText size={16} className="text-brand" />
                  <span className="file-name">{f.name}</span>
                  <span className="file-size">{f.size}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: 1-Click Demo Vendors for Hackathon Judges */}
        <div className="upload-right-col">
          <div className="demo-vendors-card">
            <div className="demo-header">
              <Sparkles size={18} className="text-brand" />
              <div>
                <h3>Test with Pre-Loaded Vendor Filings</h3>
                <p>Click any scenario below to see how TenderGuard AI handles different compliance outcomes.</p>
              </div>
            </div>

            <div className="demo-vendor-options">
              {/* Option 1: Fully Compliant */}
              <div 
                className={`vendor-choice-card choice-compliant ${selectedVendor?.id === 'vendor-1' ? 'choice-selected' : ''}`}
                onClick={() => startScanningSimulation(MOCK_VENDORS[0])}
              >
                <div className="choice-top">
                  <div className="choice-badge badge-pass">
                    <CheckCircle2 size={14} />
                    <span>Scenario 1: Fully Compliant</span>
                  </div>
                  <span className="choice-speed">4.8s audit</span>
                </div>

                <h4 className="vendor-title">TechNova Infotech Pvt. Ltd.</h4>
                <p className="vendor-summary">
                  All 5 documents valid. PAN matches GSTIN. Qualifies for MSME EMD fee waiver and DPIIT startup turnover exemption.
                </p>

                <div className="choice-footer">
                  <span className="highlight-tag text-success">✓ 100% Eligible for Bid Opening</span>
                  <button className="btn-text">
                    <span>Audit This Vendor</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>

              {/* Option 2: Disqualified (Expired GST + PAN Mismatch) */}
              <div 
                className={`vendor-choice-card choice-rejected ${selectedVendor?.id === 'vendor-2' ? 'choice-selected' : ''}`}
                onClick={() => startScanningSimulation(MOCK_VENDORS[1])}
              >
                <div className="choice-top">
                  <div className="choice-badge badge-fail">
                    <XCircle size={14} />
                    <span>Scenario 2: Disqualified (Fatal Errors)</span>
                  </div>
                  <span className="choice-speed">3.9s audit</span>
                </div>

                <h4 className="vendor-title">Apex Global Systems Ltd.</h4>
                <p className="vendor-summary">
                  GST certificate cancelled in Jan 2024. PAN card number (BBACA...) does not match GSTIN embedded PAN (AAACA...).
                </p>

                <div className="choice-footer">
                  <span className="highlight-tag text-danger">✕ Flagged for Immediate Disqualification</span>
                  <button className="btn-text">
                    <span>Audit This Vendor</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>

              {/* Option 3: Requires Human Review */}
              <div 
                className={`vendor-choice-card choice-review ${selectedVendor?.id === 'vendor-3' ? 'choice-selected' : ''}`}
                onClick={() => startScanningSimulation(MOCK_VENDORS[2])}
              >
                <div className="choice-top">
                  <div className="choice-badge badge-review">
                    <AlertTriangle size={14} />
                    <span>Scenario 3: Requires Human Review</span>
                  </div>
                  <span className="choice-speed">4.1s audit</span>
                </div>

                <h4 className="vendor-title">Bharat Cloud Dynamics LLP</h4>
                <p className="vendor-summary">
                  All legal IDs match, but OEM rubber seal is faint (64% confidence) and Startup India 10-year period expires within 60 days.
                </p>

                <div className="choice-footer">
                  <span className="highlight-tag text-warning">⚠️ Routed to Human Review Officer</span>
                  <button className="btn-text">
                    <span>Audit This Vendor</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
