import React, { useState } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  Send, 
  UserCheck, 
  ShieldAlert, 
  Eye, 
  Sparkles,
  HelpCircle,
  FileText,
  CornerDownRight
} from 'lucide-react';
import DocumentRenderer from './DocumentRenderer';
import confetti from 'canvas-confetti';

export default function EvidenceInspector({ 
  vendor, 
  activeDocId, 
  setActiveDocId,
  onBackToDashboard 
}) {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [activeBoxId, setActiveBoxId] = useState(null);
  const [officerNotes, setOfficerNotes] = useState('');
  const [officerActionTaken, setOfficerActionTaken] = useState(null);
  const [showClarificationModal, setShowClarificationModal] = useState(false);

  if (!vendor) return <div>No vendor selected</div>;

  const activeDoc = vendor.documents.find(d => d.id === activeDocId) || vendor.documents[0];

  const handleZoom = (delta) => {
    setZoomLevel(prev => Math.min(1.6, Math.max(0.7, Number((prev + delta).toFixed(1)))));
  };

  const handleResetZoom = () => setZoomLevel(1);

  const handleOfficerApprove = () => {
    setOfficerActionTaken('APPROVED');
    confetti({
      particleCount: 50,
      spread: 60,
      origin: { y: 0.6 }
    });
  };

  const handleOfficerDisqualify = () => {
    setOfficerActionTaken('DISQUALIFIED');
  };

  const handleRequestClarification = () => {
    setShowClarificationModal(true);
  };

  return (
    <div className="inspector-view-container">
      {/* Top Document Category Selector Tabs */}
      <div className="inspector-top-bar">
        <div className="doc-selector-tabs">
          {vendor.documents.map((doc) => {
            const isActive = doc.id === activeDoc.id;
            return (
              <button
                key={doc.id}
                className={`doc-tab-btn ${isActive ? 'doc-tab-active' : ''}`}
                onClick={() => {
                  setActiveDocId(doc.id);
                  setActiveBoxId(null);
                  setOfficerActionTaken(null);
                }}
              >
                <span className="tab-status-icon">
                  {doc.status === 'COMPLIANT' && <CheckCircle2 size={15} className="text-success" />}
                  {doc.status === 'NON_COMPLIANT' && <XCircle size={15} className="text-danger" />}
                  {doc.status === 'REQUIRES_REVIEW' && <AlertTriangle size={15} className="text-warning" />}
                </span>
                <span className="tab-title">{doc.title}</span>
              </button>
            );
          })}
        </div>

        {/* Zoom & View Controls */}
        <div className="zoom-controls-strip">
          <button className="ctrl-btn" onClick={() => handleZoom(-0.1)} title="Zoom Out">
            <ZoomOut size={15} />
          </button>
          <span className="zoom-indicator font-mono">{Math.round(zoomLevel * 100)}%</span>
          <button className="ctrl-btn" onClick={() => handleZoom(0.1)} title="Zoom In">
            <ZoomIn size={15} />
          </button>
          <button className="ctrl-btn" onClick={handleResetZoom} title="Reset View">
            <RotateCcw size={14} />
          </button>
        </div>
      </div>

      {/* Main 3-Column Layout: Left Field List | Center Canvas | Right Plain English Explanation */}
      <div className="inspector-3col-layout">
        {/* Left Column: Extracted Metadata Fields */}
        <div className="inspector-left-panel">
          <div className="panel-header-box">
            <span className="panel-tag">Extracted Entities</span>
            <h3>{activeDoc.title}</h3>
            <span className="form-type-badge font-mono">{activeDoc.formType}</span>
          </div>

          <div className="doc-status-banner-card">
            <div className="banner-top">
              <span className="banner-k">AI Verification Verdict:</span>
              <span className={`status-chip chip-${activeDoc.status.toLowerCase()}`}>
                {activeDoc.status === 'COMPLIANT' && "✓ COMPLIANT"}
                {activeDoc.status === 'NON_COMPLIANT' && "✕ REJECTED"}
                {activeDoc.status === 'REQUIRES_REVIEW' && "⚠ REQUIRES REVIEW"}
              </span>
            </div>
            <div className="banner-confidence">
              <span>Confidence:</span>
              <strong className="font-mono text-brand">{activeDoc.evaluation.confidence}</strong>
            </div>
          </div>

          <div className="extracted-fields-list">
            <div className="fields-title">Click a field to highlight on document:</div>
            {Object.entries(activeDoc.extractedData).map(([key, val]) => {
              const formattedKey = key
                .replace(/([A-Z])/g, ' $1')
                .replace(/^./, str => str.toUpperCase());
              
              const matchingBox = activeDoc.boundingBoxes?.find(b => 
                b.label.toLowerCase().includes(key.toLowerCase()) || 
                key.toLowerCase().includes(b.label.toLowerCase().split(' ')[0])
              );

              return (
                <div 
                  key={key} 
                  className={`field-row-card ${matchingBox && activeBoxId === matchingBox.id ? 'field-selected' : ''}`}
                  onClick={() => {
                    if (matchingBox) setActiveBoxId(matchingBox.id);
                  }}
                >
                  <div className="field-k-row">
                    <span className="field-label">{formattedKey}</span>
                    {matchingBox && (
                      <span className="field-trace-tag font-mono">
                        <Eye size={10} /> Page {activeDoc.evaluation.pageNumber}
                      </span>
                    )}
                  </div>
                  <div className="field-v-row font-mono">
                    {String(val)}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Center Column: High-Resolution Document Canvas with Bounding Boxes */}
        <div className="inspector-center-canvas">
          <div className="canvas-header-bar">
            <div className="evidence-trace-indicator">
              <Sparkles size={14} className="text-brand" />
              <span>Visual Evidence Trace: <strong>Page {activeDoc.evaluation.pageNumber} of 1</strong></span>
            </div>
            <div className="canvas-hint">
              <span>Click any colored box to view why it passed or failed</span>
            </div>
          </div>

          <div className="canvas-viewport">
            <DocumentRenderer 
              documentData={activeDoc} 
              activeBoxId={activeBoxId}
              onSelectBox={(boxId) => setActiveBoxId(boxId)}
              zoomLevel={zoomLevel}
            />
          </div>
        </div>

        {/* Right Column: Explainable AI "Why" Drawer & Human Officer Sign-Off */}
        <div className="inspector-right-panel">
          <div className="panel-header-box">
            <span className="panel-tag">Explainable AI Core</span>
            <h3>Why Was This Decision Made?</h3>
            <p className="panel-sub">Simple English explanation generated for audit transparency.</p>
          </div>

          {/* Plain English Reason Box */}
          <div className={`explain-reason-card reason-${activeDoc.status.toLowerCase()}`}>
            <div className="reason-top">
              <span className="reason-label">Plain English Explanation:</span>
            </div>
            <p className="reason-text">
              {activeDoc.evaluation.simpleReason}
            </p>
          </div>

          {/* Rule Cross-Reference Box */}
          <div className="rule-comparison-card">
            <h4>Checklist Cross-Reference:</h4>
            <div className="rule-comp-row">
              <span className="rk">GeM Tender Rule:</span>
              <span className="rv">{activeDoc.evaluation.expectedRule}</span>
            </div>
            <div className="rule-comp-row">
              <span className="rk">AI Extracted Status:</span>
              <span className="rv font-mono font-bold">{activeDoc.status}</span>
            </div>
          </div>

          {/* Human-in-the-Loop Reviewer Actions */}
          <div className="human-officer-panel">
            <div className="hop-header">
              <UserCheck size={18} className="text-brand" />
              <h4>Human Procurement Officer Sign-Off</h4>
            </div>
            <p className="hop-sub">
              Ambiguous cases and vendor appeals are decided by the officer. AI does not disqualify without human audit trail.
            </p>

            {officerActionTaken ? (
              <div className={`officer-outcome-badge badge-${officerActionTaken.toLowerCase()}`}>
                <CheckCircle2 size={16} />
                <span>Officer Decision Recorded: <strong>{officerActionTaken}</strong></span>
              </div>
            ) : (
              <div className="officer-actions-grid">
                <button 
                  className="btn btn-sm btn-outline-success"
                  onClick={handleOfficerApprove}
                >
                  ✓ Approve with Exemption
                </button>
                <button 
                  className="btn btn-sm btn-outline-danger"
                  onClick={handleOfficerDisqualify}
                >
                  ✕ Confirm Disqualification
                </button>
                <button 
                  className="btn btn-sm btn-outline-warning col-span-2"
                  onClick={handleRequestClarification}
                >
                  ✉ Request Clarification (48h Notice)
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Clarification Request Modal */}
      {showClarificationModal && (
        <div className="modal-backdrop" onClick={() => setShowClarificationModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title-with-icon">
                <div className="icon-wrap tender-blue">
                  <Send size={20} />
                </div>
                <div>
                  <h3>Send Clarification Notice to Vendor</h3>
                  <p className="modal-sub">Drafted in simple English according to GFR procurement guidelines</p>
                </div>
              </div>
              <button className="modal-close-btn" onClick={() => setShowClarificationModal(false)}>×</button>
            </div>

            <div className="modal-body">
              <div className="clarification-draft-box">
                <div className="email-row">
                  <span className="e-k">To:</span>
                  <span className="e-v font-mono">compliance@{vendor.name.toLowerCase().replace(/[^a-z]/g, '')}.com</span>
                </div>
                <div className="email-row">
                  <span className="e-k">Subject:</span>
                  <span className="e-v font-bold">Clarification Notice: Tender Ref {vendor.tenderId || 'GeM/2026/B/89412'} — {activeDoc.title}</span>
                </div>
                <div className="email-body-text">
                  <p>Dear {vendor.name},</p>
                  <p>
                    During automated compliance screening of your bid for Tender <strong>GeM/2026/B/89412</strong>, the following issue was flagged on your <strong>{activeDoc.title}</strong>:
                  </p>
                  <div className="flag-quote-box">
                    "{activeDoc.evaluation.simpleReason}"
                  </div>
                  <p>
                    Please upload an authenticated, high-resolution copy within <strong>48 hours</strong> via the GeM Vendor Grievance Portal to avoid technical disqualification.
                  </p>
                  <p>Regards,<br />Procurement Officer, MeitY / GeM Portal</p>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowClarificationModal(false)}>
                Cancel
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => {
                  setShowClarificationModal(false);
                  setOfficerActionTaken('CLARIFICATION REQUESTED');
                }}
              >
                Send Official Notice
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
