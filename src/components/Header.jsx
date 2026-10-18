import React, { useState } from 'react';
import { Shield, CheckCircle2, AlertTriangle, FileText, Lock, ExternalLink, Info, Award, LogOut, UserCheck } from 'lucide-react';
import { TENDER_DETAILS } from '../data/mockVendors';

export default function Header({ activeTab, setActiveTab, selectedVendor, onResetToUpload, currentUser, onLogout }) {
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [showTenderModal, setShowTenderModal] = useState(false);

  return (
    <header className="app-header">
      {/* Top Banner: Official GeM / Ministry Context */}
      <div className="gov-meta-bar">
        <div className="gov-meta-container">
          <div className="gov-badge-group">
            <span className="gov-flag">🇮🇳</span>
            <span className="gov-portal-tag">Government e-Marketplace (GeM 4.0)</span>
            <span className="gov-dot">·</span>
            <span className="gov-dept">{TENDER_DETAILS.department}</span>
          </div>

          <div className="gov-meta-actions">
            <button 
              className="meta-link-btn"
              onClick={() => setShowTenderModal(true)}
              title="View tender specifications & rules"
            >
              <Info size={14} />
              <span>Tender Ref: <strong>{TENDER_DETAILS.tenderId}</strong></span>
            </button>

            <button 
              className="privacy-badge-pill"
              onClick={() => setShowPrivacyModal(true)}
              title="Click to view zero-retention data privacy guarantees"
            >
              <Lock size={12} className="lock-icon" />
              <span>Zero-Retention Auditing</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Brand & Category Navigation Bar */}
      <div className="main-nav-container">
        <div className="brand-zone">
          <div className="brand-logo-custom-wrap">
            <img 
              src="/tenderguard-logo.jpg" 
              alt="TenderGuard Logo" 
              className="brand-logo-img" 
            />
          </div>
          <div className="brand-text">
            <div className="brand-name">
              TenderGuard <span className="ai-badge">AI</span>
            </div>
            <div className="brand-tagline">Explainable Vendor Compliance for Public Procurement</div>
          </div>
        </div>

        {/* Clean Category Navigation Tabs */}
        <nav className="category-tabs" aria-label="Main Navigation">
          <button 
            className={`tab-item ${activeTab === 'guide' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('guide')}
            id="nav-tab-guide"
          >
            <span className="tab-number">1</span>
            <span className="tab-label">Before You Upload</span>
            <span className="tab-sub">Rules & Checklist</span>
          </button>

          <button 
            className={`tab-item ${activeTab === 'upload' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('upload')}
            id="nav-tab-upload"
          >
            <span className="tab-number">2</span>
            <span className="tab-label">Upload & Scan</span>
            <span className="tab-sub">Test Filings</span>
          </button>

          <button 
            className={`tab-item ${activeTab === 'dashboard' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
            id="nav-tab-dashboard"
          >
            <span className="tab-number">3</span>
            <span className="tab-label">Compliance Overview</span>
            <span className="tab-sub">Eligibility Status</span>
          </button>

          <button 
            className={`tab-item ${activeTab === 'inspector' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('inspector')}
            id="nav-tab-inspector"
          >
            <span className="tab-number">4</span>
            <span className="tab-label">Explainable Visual Proof</span>
            <span className="tab-sub">Bounding Box Trace</span>
          </button>

          <button 
            className={`tab-item ${activeTab === 'export' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('export')}
            id="nav-tab-export"
          >
            <span className="tab-number">5</span>
            <span className="tab-label">Audit Report</span>
            <span className="tab-sub">Official Certificate</span>
          </button>
        </nav>

        {/* Right Actions: Active Bidder & User Badge */}
        <div className="header-right-actions">
          {selectedVendor && (
            <div className="active-bidder-pill">
              <span className="label">Auditing:</span>
              <span className="vendor-name-trunc" title={selectedVendor.name}>{selectedVendor.name}</span>
              <span className={`status-dot dot-${selectedVendor.overallStatus.toLowerCase()}`}></span>
            </div>
          )}

          {currentUser && (
            <div className="user-profile-pill">
              <div className="user-avatar-dot">
                <UserCheck size={13} />
              </div>
              <div className="user-info-text">
                <span className="user-name">{currentUser.name}</span>
                <span className="user-role-badge">{currentUser.isGuest ? 'Guest Mode' : currentUser.role}</span>
              </div>
              {onLogout && (
                <button 
                  className="user-logout-btn" 
                  onClick={onLogout}
                  title="Sign out / Switch user"
                >
                  <LogOut size={13} />
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Zero Retention Privacy Modal */}
      {showPrivacyModal && (
        <div className="modal-backdrop" onClick={() => setShowPrivacyModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title-with-icon">
                <div className="icon-wrap lock-green">
                  <Lock size={20} />
                </div>
                <div>
                  <h3>Strict Zero-Retention Data Privacy Standard</h3>
                  <p className="modal-sub">How TenderGuard AI protects vendor proprietary data and tender integrity</p>
                </div>
              </div>
              <button className="modal-close-btn" onClick={() => setShowPrivacyModal(false)}>×</button>
            </div>

            <div className="modal-body">
              <div className="privacy-feature-list">
                <div className="privacy-feature-item">
                  <div className="p-num">01</div>
                  <div>
                    <h4>Volatile RAM Processing Only</h4>
                    <p>Uploaded PDFs and images are processed strictly in ephemeral RAM buffers. Documents are never written to permanent disk storage.</p>
                  </div>
                </div>

                <div className="privacy-feature-item">
                  <div className="p-num">02</div>
                  <div>
                    <h4>Zero Model Retraining</h4>
                    <p>Vendor filings, PAN numbers, balance sheets, and proprietary pricing are NEVER used to fine-tune or train third-party foundation models.</p>
                  </div>
                </div>

                <div className="privacy-feature-item">
                  <div className="p-num">03</div>
                  <div>
                    <h4>Cryptographic Audit Fingerprinting</h4>
                    <p>Upon verification, a one-way SHA-256 hash of the document is generated to create an immutable audit trail without storing the document itself.</p>
                  </div>
                </div>
              </div>

              <div className="privacy-alert-box">
                <CheckCircle2 size={18} className="text-success" />
                <span>Fully compliant with <strong>India Digital Personal Data Protection (DPDP) Act, 2023</strong> and GeM procurement confidentiality protocols.</span>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn btn-primary" onClick={() => setShowPrivacyModal(false)}>
                Understood & Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tender Details Modal */}
      {showTenderModal && (
        <div className="modal-backdrop" onClick={() => setShowTenderModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title-with-icon">
                <div className="icon-wrap tender-blue">
                  <FileText size={20} />
                </div>
                <div>
                  <h3>Procurement Bid Specifications</h3>
                  <p className="modal-sub">{TENDER_DETAILS.title}</p>
                </div>
              </div>
              <button className="modal-close-btn" onClick={() => setShowTenderModal(false)}>×</button>
            </div>

            <div className="modal-body">
              <div className="tender-specs-grid">
                <div className="spec-row">
                  <span className="spec-k">Tender ID:</span>
                  <span className="spec-v font-mono font-bold">{TENDER_DETAILS.tenderId}</span>
                </div>
                <div className="spec-row">
                  <span className="spec-k">Procuring Dept:</span>
                  <span className="spec-v">{TENDER_DETAILS.department}</span>
                </div>
                <div className="spec-row">
                  <span className="spec-k">Submission Deadline:</span>
                  <span className="spec-v font-bold">{TENDER_DETAILS.submissionDeadline}</span>
                </div>
                <div className="spec-row">
                  <span className="spec-k">Validity Period:</span>
                  <span className="spec-v text-success">{TENDER_DETAILS.validityRequirement}</span>
                </div>
                <div className="spec-row">
                  <span className="spec-k">Turnover Criteria:</span>
                  <span className="spec-v">{TENDER_DETAILS.minimumTurnover}</span>
                </div>
              </div>

              <div className="tender-doc-list">
                <h4>Mandatory Checklists Verified by AI:</h4>
                <ul>
                  {TENDER_DETAILS.mandatoryDocuments.map((doc, idx) => (
                    <li key={idx}>
                      <CheckCircle2 size={14} className="text-success" />
                      <span>{doc}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowTenderModal(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
