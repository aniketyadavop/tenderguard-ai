import React, { useState } from 'react';
import { 
  CheckCircle2, 
  AlertCircle, 
  FileCheck2, 
  HelpCircle, 
  Calendar, 
  CreditCard, 
  Building2, 
  Rocket, 
  FileBadge, 
  ArrowRight,
  ShieldAlert,
  Sparkles,
  Check,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { PRE_SUBMISSION_GUIDE } from '../data/mockVendors';

export default function PreSubmissionGuide({ onProceedToUpload }) {
  // Category sub-navigation to keep page light and uncrowded
  const [activeCategory, setActiveCategory] = useState('steps'); // 'steps' | 'docs' | 'rejections' | 'checklist'
  const [openFaq, setOpenFaq] = useState(0);

  // Interactive self-check state
  const [checks, setChecks] = useState({
    expiry: false,
    panMatch: false,
    oemRef: false,
    clearScan: false,
    msmeLatest: false
  });

  const toggleCheck = (key) => {
    setChecks(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const completedCount = Object.values(checks).filter(Boolean).length;
  const readinessPercent = Math.round((completedCount / 5) * 100);

  return (
    <div className="guide-view-container">
      {/* Category Hero / Header */}
      <div className="section-header">
        <div className="header-badge-chip">
          <Sparkles size={14} />
          <span>Vendor Onboarding & Guidance</span>
        </div>
        <h1 className="section-title">Everything You Need Before Submitting</h1>
        <p className="section-subtitle">
          Government tenders have strict compliance rules. Follow this simple guide to ensure your filing passes AI verification on the first try without administrative delays.
        </p>

        {/* Sub-Category Switcher: Keeps content clean and organized */}
        <div className="sub-category-pills">
          <button 
            className={`sub-pill ${activeCategory === 'steps' ? 'sub-pill-active' : ''}`}
            onClick={() => setActiveCategory('steps')}
          >
            <span className="step-tag">1</span>
            <span>4 Simple Preparation Steps</span>
          </button>

          <button 
            className={`sub-pill ${activeCategory === 'docs' ? 'sub-pill-active' : ''}`}
            onClick={() => setActiveCategory('docs')}
          >
            <span className="step-tag">2</span>
            <span>Required Documents List</span>
          </button>

          <button 
            className={`sub-pill ${activeCategory === 'rejections' ? 'sub-pill-active' : ''}`}
            onClick={() => setActiveCategory('rejections')}
          >
            <span className="step-tag">3</span>
            <span>Why Documents Get Rejected</span>
          </button>

          <button 
            className={`sub-pill ${activeCategory === 'checklist' ? 'sub-pill-active' : ''}`}
            onClick={() => setActiveCategory('checklist')}
          >
            <span className="step-tag">4</span>
            <span>Pre-Flight Self-Check ({readinessPercent}%)</span>
          </button>
        </div>
      </div>

      {/* CATEGORY 1: 4 SIMPLE STEPS */}
      {activeCategory === 'steps' && (
        <div className="guide-content-block">
          <div className="steps-cards-grid">
            {PRE_SUBMISSION_GUIDE.steps.map((item) => (
              <div key={item.step} className="step-card">
                <div className="step-card-top">
                  <div className="step-number-bubble">{item.step}</div>
                  <div className="step-icon-wrap">
                    {item.step === 1 && <Calendar size={20} />}
                    {item.step === 2 && <CreditCard size={20} />}
                    {item.step === 3 && <FileBadge size={20} />}
                    {item.step === 4 && <FileCheck2 size={20} />}
                  </div>
                </div>

                <h3 className="step-card-title">{item.title}</h3>
                <p className="step-card-summary">{item.summary}</p>

                <div className="step-card-tips">
                  <span className="tips-label">Quick check:</span>
                  <ul>
                    {item.tips.map((tip, idx) => (
                      <li key={idx}>
                        <CheckCircle2 size={14} className="text-success check-bullet" />
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>

          <div className="guide-next-banner">
            <div>
              <h4>Ready to test your documents?</h4>
              <p>You can upload your files or test with our pre-loaded sample vendor filings.</p>
            </div>
            <button className="btn btn-primary" onClick={onProceedToUpload}>
              <span>Go to Document Upload</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* CATEGORY 2: REQUIRED DOCUMENTS LIST */}
      {activeCategory === 'docs' && (
        <div className="guide-content-block">
          <div className="doc-list-grid">
            {PRE_SUBMISSION_GUIDE.requiredDocumentsList.map((doc, idx) => (
              <div key={idx} className="required-doc-card">
                <div className="rd-header">
                  <div className="rd-title-group">
                    <span className="rd-icon">
                      {idx === 0 && <Building2 size={18} />}
                      {idx === 1 && <CreditCard size={18} />}
                      {idx === 2 && <FileCheck2 size={18} />}
                      {idx === 3 && <Rocket size={18} />}
                      {idx === 4 && <FileBadge size={18} />}
                    </span>
                    <h4>{doc.name}</h4>
                  </div>
                  <span className={`rd-badge ${doc.mandatory ? 'badge-mandatory' : 'badge-optional'}`}>
                    {doc.mandatory ? 'Mandatory' : 'Optional Exemption'}
                  </span>
                </div>

                <p className="rd-purpose"><strong>Purpose:</strong> {doc.purpose}</p>

                <div className="rd-rule-box">
                  <span className="rd-rule-tag">Verification Rule:</span>
                  <span className="rd-rule-text">{doc.rule}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="guide-callout-info">
            <HelpCircle size={18} className="text-brand" />
            <div>
              <strong>What if a document is optional?</strong>
              <p>Startup India and MSME certificates are optional. If you don't submit them, you must satisfy the standard ₹5.00 Crore turnover and Earnest Money Deposit (EMD) requirements.</p>
            </div>
          </div>
        </div>
      )}

      {/* CATEGORY 3: WHY DOCUMENTS GET REJECTED */}
      {activeCategory === 'rejections' && (
        <div className="guide-content-block">
          <div className="rejection-intro-card">
            <ShieldAlert size={22} className="text-danger" />
            <div>
              <h3>Over 80% of vendor disqualifications are due to simple, avoidable errors</h3>
              <p>Here are the top 5 reasons government procurement officers reject filings, explained in plain English, and how to avoid them.</p>
            </div>
          </div>

          <div className="rejection-accordion">
            {PRE_SUBMISSION_GUIDE.rejectionReasons.map((item, index) => {
              const isOpen = openFaq === index;
              return (
                <div key={index} className={`rejection-card ${isOpen ? 'rej-open' : ''}`}>
                  <button 
                    className="rejection-card-header"
                    onClick={() => setOpenFaq(isOpen ? -1 : index)}
                  >
                    <div className="rej-left">
                      <span className="rej-rank">#{item.rank}</span>
                      <span className="rej-title">{item.title}</span>
                      <span className="rej-percent">{item.percentage}</span>
                    </div>
                    <div className="rej-toggle">
                      {isOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </div>
                  </button>

                  {isOpen && (
                    <div className="rejection-card-body">
                      <div className="why-box">
                        <span className="box-title">Why it happens (Plain English):</span>
                        <p>{item.plainExplanation}</p>
                      </div>

                      <div className="how-fix-box">
                        <span className="box-title">How to avoid rejection:</span>
                        <p>{item.howToAvoid}</p>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* CATEGORY 4: INTERACTIVE PRE-FLIGHT CHECKLIST */}
      {activeCategory === 'checklist' && (
        <div className="guide-content-block">
          <div className="readiness-meter-card">
            <div className="meter-left">
              <h3>Pre-Flight Readiness Checker</h3>
              <p>Tick each box to verify your folder before submitting to TenderGuard AI.</p>
            </div>
            <div className="meter-right">
              <div className="meter-progress-circle">
                <span className="meter-num">{readinessPercent}%</span>
                <span className="meter-sub">Ready</span>
              </div>
            </div>
          </div>

          <div className="checklist-items-box">
            <label className={`check-item ${checks.expiry ? 'item-checked' : ''}`}>
              <input 
                type="checkbox" 
                checked={checks.expiry} 
                onChange={() => toggleCheck('expiry')} 
              />
              <div className="check-text">
                <strong>1. All my certificates are active through at least 30 Nov 2026</strong>
                <span>Checked my GSTIN and registration status on government portals.</span>
              </div>
            </label>

            <label className={`check-item ${checks.panMatch ? 'item-checked' : ''}`}>
              <input 
                type="checkbox" 
                checked={checks.panMatch} 
                onChange={() => toggleCheck('panMatch')} 
              />
              <div className="check-text">
                <strong>2. My PAN number matches digits 3 to 12 of my GSTIN</strong>
                <span>I am submitting the company PAN, not an unrelated individual's PAN.</span>
              </div>
            </label>

            <label className={`check-item ${checks.oemRef ? 'item-checked' : ''}`}>
              <input 
                type="checkbox" 
                checked={checks.oemRef} 
                onChange={() => toggleCheck('oemRef')} 
              />
              <div className="check-text">
                <strong>3. OEM Authorization Letter cites Tender Ref: GeM/2026/B/89412</strong>
                <span>The letter contains the exact bid reference and has a clear authorized stamp.</span>
              </div>
            </label>

            <label className={`check-item ${checks.clearScan ? 'item-checked' : ''}`}>
              <input 
                type="checkbox" 
                checked={checks.clearScan} 
                onChange={() => toggleCheck('clearScan')} 
              />
              <div className="check-text">
                <strong>4. All files are clear, high-resolution PDFs or images (under 25MB)</strong>
                <span>No cut-off corners, blurry text, or illegible digital signatures.</span>
              </div>
            </label>

            <label className={`check-item ${checks.msmeLatest ? 'item-checked' : ''}`}>
              <input 
                type="checkbox" 
                checked={checks.msmeLatest} 
                onChange={() => toggleCheck('msmeLatest')} 
              />
              <div className="check-text">
                <strong>5. If claiming EMD exemption, I have attached my active Udyam Certificate</strong>
                <span>Registered under Micro or Small enterprise category for services/goods.</span>
              </div>
            </label>
          </div>

          <div className="checklist-footer">
            <div className="footer-status">
              {completedCount === 5 ? (
                <span className="text-success font-bold">🎉 Outstanding! Your folder is 100% ready for verification.</span>
              ) : (
                <span className="text-muted">You have checked {completedCount} of 5 items.</span>
              )}
            </div>
            <button 
              className="btn btn-primary"
              onClick={onProceedToUpload}
            >
              <span>Continue to Upload</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
