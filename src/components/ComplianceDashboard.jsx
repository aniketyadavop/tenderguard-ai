import React from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Clock, 
  ShieldCheck, 
  FileSearch, 
  ArrowRight, 
  Sparkles,
  ExternalLink,
  Award,
  AlertCircle,
  FileText
} from 'lucide-react';
import { TENDER_DETAILS } from '../data/mockVendors';

export default function ComplianceDashboard({ 
  vendor, 
  onInspectDocument, 
  onViewReport, 
  onChangeVendor 
}) {
  if (!vendor) {
    return (
      <div className="empty-dashboard-state">
        <FileSearch size={48} className="empty-icon" />
        <h2>No Vendor Audit Loaded</h2>
        <p>Please select a vendor or upload documents to generate a compliance audit.</p>
        <button className="btn btn-primary" onClick={onChangeVendor}>
          Choose a Vendor Filing
        </button>
      </div>
    );
  }

  const isCompliant = vendor.overallStatus === 'COMPLIANT';
  const isRejected = vendor.overallStatus === 'NON_COMPLIANT';
  const isReview = vendor.overallStatus === 'REQUIRES_REVIEW';

  const compliantDocs = vendor.documents.filter(d => d.status === 'COMPLIANT');
  const nonCompliantDocs = vendor.documents.filter(d => d.status === 'NON_COMPLIANT');
  const reviewDocs = vendor.documents.filter(d => d.status === 'REQUIRES_REVIEW');

  return (
    <div className="dashboard-view-container">
      {/* Top Banner: Bidder Summary Card */}
      <div className={`verdict-hero-card verdict-${vendor.overallStatus.toLowerCase()}`}>
        <div className="verdict-main-row">
          <div className="verdict-status-box">
            <div className="status-icon-bubble">
              {isCompliant && <CheckCircle2 size={32} />}
              {isRejected && <XCircle size={32} />}
              {isReview && <AlertTriangle size={32} />}
            </div>
            <div>
              <div className="verdict-tag">OVERALL AUDIT VERDICT</div>
              <h2 className="verdict-title">
                {isCompliant && "Compliant — Recommended for Financial Bid Opening"}
                {isRejected && "Non-Compliant — Disqualified on Technical Grounds"}
                {isReview && "Requires Review — Flagged for Procurement Officer"}
              </h2>
              <p className="verdict-explainer">
                {vendor.summary}
              </p>
            </div>
          </div>

          <div className="verdict-actions">
            <button 
              className="btn btn-primary btn-lg"
              onClick={() => onInspectDocument(vendor.documents[0].id)}
            >
              <FileSearch size={18} />
              <span>Inspect Visual Evidence</span>
              <ArrowRight size={16} />
            </button>
            <button 
              className="btn btn-secondary"
              onClick={onViewReport}
            >
              <FileText size={16} />
              <span>View Audit Certificate</span>
            </button>
          </div>
        </div>

        {/* Metric Badges */}
        <div className="verdict-stats-strip">
          <div className="stat-pill">
            <span className="stat-k">Bidder Name:</span>
            <span className="stat-v font-bold">{vendor.name}</span>
          </div>
          <div className="stat-pill">
            <span className="stat-k">AI Extraction Accuracy:</span>
            <span className="stat-v text-success font-bold font-mono">{vendor.confidenceScore}%</span>
          </div>
          <div className="stat-pill">
            <span className="stat-k">Audit Time:</span>
            <span className="stat-v font-mono">{vendor.auditTimeSeconds}s <span className="stat-dim">(vs 45m manual)</span></span>
          </div>
          <div className="stat-pill">
            <span className="stat-k">Documents Audited:</span>
            <span className="stat-v font-bold">{vendor.documents.length} of 5</span>
          </div>
        </div>
      </div>

      {/* Categorized Compliance Sections (Clean, uncluttered, simple English) */}
      <div className="dashboard-categories-grid">
        {/* Category 1: Why It Was Rejected / Flagged (If Any) */}
        {(isRejected || isReview) && (
          <div className="dashboard-cat-card card-warning-zone">
            <div className="cat-card-header">
              <div className="cat-title-group">
                <AlertCircle className={isRejected ? "text-danger" : "text-warning"} size={20} />
                <h3>
                  {isRejected ? "Critical Issues Causing Disqualification" : "Items Requiring Human Officer Verification"}
                </h3>
              </div>
              <span className={`cat-count-badge ${isRejected ? 'badge-danger' : 'badge-warning'}`}>
                {isRejected ? `${nonCompliantDocs.length} Disqualification Flags` : `${reviewDocs.length} Attention Flags`}
              </span>
            </div>

            <p className="cat-subtitle">
              TenderGuard AI explains exactly why these items were flagged in plain English with direct visual coordinates:
            </p>

            <div className="flagged-items-list">
              {vendor.disqualificationReasons.map((issue, idx) => (
                <div key={idx} className="flagged-item-box box-danger">
                  <div className="flag-top">
                    <span className="doc-pill text-danger">{issue.document}</span>
                    <span className="code-pill font-mono">{issue.code}</span>
                  </div>
                  <h4 className="flag-headline">{issue.title}</h4>
                  <p className="flag-simple-text">{issue.simpleReason}</p>
                  <button 
                    className="btn-inspect-link"
                    onClick={() => {
                      const target = vendor.documents.find(d => d.title.includes(issue.document.split(' ')[0]));
                      if (target) onInspectDocument(target.id);
                    }}
                  >
                    <span>View Red Bounding Box on Original Document</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              ))}

              {vendor.reviewNotes.map((note, idx) => (
                <div key={idx} className="flagged-item-box box-warning">
                  <div className="flag-top">
                    <span className="doc-pill text-warning">{note.document}</span>
                    <span className="code-pill font-mono">{note.field}</span>
                  </div>
                  <h4 className="flag-headline">Flagged for Human Eye Check</h4>
                  <p className="flag-simple-text">{note.simpleReason}</p>
                  <button 
                    className="btn-inspect-link text-warning"
                    onClick={() => {
                      const target = vendor.documents.find(d => d.title.includes(note.document.split(' ')[0]));
                      if (target) onInspectDocument(target.id);
                    }}
                  >
                    <span>View Highlighted Area on Document</span>
                    <ArrowRight size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Category 2: Verified Compliant Items */}
        <div className="dashboard-cat-card card-passed-zone">
          <div className="cat-card-header">
            <div className="cat-title-group">
              <CheckCircle2 className="text-success" size={20} />
              <h3>Verified Compliant Checklist</h3>
            </div>
            <span className="cat-count-badge badge-success">
              {compliantDocs.length} Verified
            </span>
          </div>

          <p className="cat-subtitle">
            These documents satisfied all legal criteria under GeM e-procurement guidelines:
          </p>

          <div className="compliant-items-list">
            {compliantDocs.map((doc) => (
              <div 
                key={doc.id} 
                className="compliant-item-row"
                onClick={() => onInspectDocument(doc.id)}
              >
                <div className="ci-left">
                  <div className="ci-icon-box">
                    <CheckCircle2 size={16} className="text-success" />
                  </div>
                  <div>
                    <div className="ci-name">{doc.title}</div>
                    <div className="ci-reason">{doc.evaluation.simpleReason}</div>
                  </div>
                </div>

                <div className="ci-right">
                  <span className="ci-confidence font-mono">{doc.evaluation.confidence} match</span>
                  <button className="btn-view-doc">Inspect</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Category 3: Statutory Exemptions & Preferences Qualified */}
        <div className="dashboard-cat-card card-exemptions-zone">
          <div className="cat-card-header">
            <div className="cat-title-group">
              <Award className="text-brand" size={20} />
              <h3>Exemptions & Price Preferences Claimed</h3>
            </div>
            <span className="cat-count-badge badge-brand">
              Public Procurement Policy
            </span>
          </div>

          <div className="exemptions-grid">
            <div className="exemption-card">
              <div className="ex-title">Earnest Money Deposit (EMD) Waiver</div>
              <div className="ex-status text-success">
                {isCompliant ? "✓ 100% Fee Exemption Granted" : "✕ Not Granted (Vendor Disqualified)"}
              </div>
              <p className="ex-desc">
                Verified via Udyam Registration. Eligible under Micro/Small Enterprise reservation clause.
              </p>
            </div>

            <div className="exemption-card">
              <div className="ex-title">Prior Turnover & Experience Exemption</div>
              <div className="ex-status text-success">
                {isCompliant ? "✓ Startup India GFR Rule 173(i) Active" : "✕ Standard ₹5 Cr Requirement Applies"}
              </div>
              <p className="ex-desc">
                Entity recognized by DPIIT within valid 10-year period.
              </p>
            </div>
          </div>

          <div className="switch-vendor-footer">
            <span className="text-muted">Want to test a different outcome?</span>
            <button className="btn btn-outline" onClick={onChangeVendor}>
              Switch Demo Vendor
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
