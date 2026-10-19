import React from 'react';

/**
 * High-fidelity SVG-based Indian Government Document Renderer
 * Renders authentic-looking certificates: GST Form REG-06, Income Tax PAN Card,
 * Udyam Registration Certificate, Startup India Recognition, and OEM MAF.
 * Includes interactive bounding boxes for explainable AI visual evidence tracing.
 */
export default function DocumentRenderer({
  documentData,
  activeBoxId,
  onSelectBox,
  zoomLevel = 1
}) {
  if (!documentData) return <div className="no-doc-selected">Select a document to inspect</div>;

  const { id, title, extractedData, status, boundingBoxes = [] } = documentData;

  const docId = (id || '').toLowerCase();
  const docTitle = (title || '').toLowerCase();
  const docType = (documentData.document_type || documentData.dtype || '').toLowerCase();
  const docForm = (documentData.formType || '').toLowerCase();

  const isGst = docId.includes('gst') || docTitle.includes('gst') || docType.includes('gst');
  const isPan = docId.includes('pan') || docTitle.includes('pan') || docType.includes('pan');
  const isUdyam = docId.includes('udyam') || docTitle.includes('udyam') || docType.includes('udyam') || docId.includes('msme') || docTitle.includes('msme') || docType.includes('msme');
  const isStartup = docId.includes('startup') || docTitle.includes('startup') || docType.includes('startup') || docId.includes('dipp') || docTitle.includes('dipp') || docForm.includes('dipp');
  const isOem = docId.includes('oem') || docTitle.includes('oem') || docType.includes('oem') || docId.includes('maf') || docTitle.includes('maf') || docType.includes('maf');

  const isFailed = status === 'NON_COMPLIANT' || status === 'FAIL' || status === 'REJECTED';
  const isReview = status === 'REQUIRES_REVIEW' || status === 'REVIEW';

  // Render specific template based on doc id / type / title
  return (
    <div 
      className="document-canvas-container"
      style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'top center' }}
    >
      <div className="document-sheet">
        {isGst && <GstTemplate data={extractedData} isCancelled={isFailed} />}
        {isPan && <PanTemplate data={extractedData} isMismatch={isFailed} />}
        {isUdyam && <UdyamTemplate data={extractedData} />}
        {isStartup && <StartupTemplate data={extractedData} isFlagged={isReview} isMissing={isFailed} />}
        {isOem && <OemTemplate data={extractedData} isFaintSeal={isReview} />}

        {!isGst && !isPan && !isUdyam && !isStartup && !isOem && (
          <div className="doc-content doc-generic-theme" style={{ padding: '2.5rem' }}>
            <div className="doc-header">
              <div className="header-text">
                <div className="gov-title">Procurement Document Verification</div>
                <div className="cert-title">{title || 'Official Submitted Document'}</div>
                <div className="form-num">{documentData.formType || documentData.document_type || 'Standard Format'}</div>
              </div>
            </div>
            <div className="doc-divider" style={{ margin: '1.5rem 0' }}></div>
            <div className="gst-grid">
              {extractedData && Object.entries(extractedData).map(([k, v]) => (
                <div className="grid-row" key={k}>
                  <span className="field-key" style={{ textTransform: 'capitalize' }}>
                    {k.replace(/([A-Z])/g, ' $1')}:
                  </span>
                  <span className="field-val font-mono font-bold">{String(v)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Visual Evidence Bounding Box Overlay Layer */}
        <div className="bounding-box-overlay">
          {boundingBoxes.map((box) => {
            const isSelected = activeBoxId === box.id;
            return (
              <div
                key={box.id}
                id={box.id}
                onClick={() => onSelectBox && onSelectBox(box.id)}
                className={`evidence-box box-${box.status} ${isSelected ? 'box-selected' : ''}`}
                style={{
                  left: `${box.x}%`,
                  top: `${box.y}%`,
                  width: `${box.width}%`,
                  height: `${box.height}%`
                }}
                title={box.text}
              >
                <span className="box-badge">
                  {box.status === 'valid' ? '✓ VERIFIED' : box.status === 'invalid' ? '✕ REJECTED' : '⚠ REVIEW'}
                </span>
                <span className="box-label-tag">{box.label}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// 1. GST Registration Certificate (Form REG-06)
function GstTemplate({ data, isCancelled }) {
  return (
    <div className="doc-content doc-gst-theme">
      <div className="doc-header">
        <div className="national-emblem">
          <svg viewBox="0 0 100 100" className="emblem-svg">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#0F172A" strokeWidth="2" />
            <circle cx="50" cy="50" r="30" fill="none" stroke="#0F172A" strokeWidth="1.5" />
            <path d="M50 5 L50 95 M5 50 L95 50" stroke="#0F172A" strokeWidth="1" strokeDasharray="2,2" />
            <text x="50" y="54" fontSize="12" textAnchor="middle" fontWeight="bold" fill="#0F172A">सत्यमेव जयते</text>
          </svg>
        </div>
        <div className="header-text">
          <div className="gov-title">Government of India / State Tax Department</div>
          <div className="cert-title">Registration Certificate</div>
          <div className="cert-subtitle">(Issued under Section 25 of the Central Goods and Services Tax Act, 2017)</div>
          <div className="form-num">FORM GST REG-06</div>
        </div>
      </div>

      <div className="doc-divider"></div>

      <div className="gst-grid">
        <div className="grid-row">
          <span className="field-key">1. GSTIN (Registration Number):</span>
          <span className="field-val highlightable font-mono font-bold">{data?.gstin || "27AABCT2341P1ZB"}</span>
        </div>
        <div className="grid-row">
          <span className="field-key">2. Legal Name of Business:</span>
          <span className="field-val highlightable font-bold">{data?.legalName || "TechNova Infotech Private Limited"}</span>
        </div>
        <div className="grid-row">
          <span className="field-key">3. Trade Name, if any:</span>
          <span className="field-val">{data?.tradeName || "TechNova Cloud Solutions"}</span>
        </div>
        <div className="grid-row">
          <span className="field-key">4. Constitution of Business:</span>
          <span className="field-val">{data?.constitutionOfBusiness || "Private Limited Company"}</span>
        </div>
        <div className="grid-row">
          <span className="field-key">5. Principal Place of Business:</span>
          <span className="field-val">{data?.principalPlace || "Plot 42, MIDC Industrial Area, Andheri East, Mumbai 400093"}</span>
        </div>
        <div className="grid-row">
          <span className="field-key">6. Date of Liability / Registration:</span>
          <span className="field-val">{data?.registrationDate || "15/04/2021"}</span>
        </div>
        <div className="grid-row">
          <span className="field-key">7. Period of Validity:</span>
          <span className={`field-val highlightable font-bold ${isCancelled ? 'text-danger' : 'text-success'}`}>
            {data?.validityPeriod || "From 15/04/2021 to Unlimited (Regular)"}
          </span>
        </div>
        <div className="grid-row">
          <span className="field-key">8. Type of Registration:</span>
          <span className="field-val">Regular Taxpayer (State: {data?.stateCode || "27 (Maharashtra)"})</span>
        </div>
      </div>

      {isCancelled && (
        <div className="doc-watermark-danger">
          CANCELLED / EXPIRED
        </div>
      )}

      <div className="doc-footer">
        <div className="qr-box">
          <div className="qr-sim">
            <div className="qr-square q1"></div>
            <div className="qr-square q2"></div>
            <div className="qr-square q3"></div>
            <div className="qr-text">GSTN SECURE VERIFY</div>
          </div>
          <div className="caption">Scannable QR Code</div>
        </div>
        <div className="sign-box">
          <div className="sign-stamp">
            <div className="ds-box">
              <span className="ds-icon">🔒</span>
              <span className="ds-text">Digitally Signed by GST Officer</span>
            </div>
            <div className="officer-name">Superintendent of Central Tax</div>
            <div className="sign-date">Verified & Authenticated</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// 2. Permanent Account Number (PAN Card)
function PanTemplate({ data, isMismatch }) {
  return (
    <div className="doc-content doc-pan-card">
      <div className="pan-inner">
        <div className="pan-header">
          <div className="pan-gov-left">
            <span>आयकर विभाग</span>
            <span className="en">INCOME TAX DEPARTMENT</span>
          </div>
          <div className="pan-emblem">
            <svg viewBox="0 0 40 40" className="pan-emblem-svg">
              <circle cx="20" cy="20" r="18" fill="none" stroke="#D97706" strokeWidth="2" />
              <text x="20" y="24" fontSize="8" textAnchor="middle" fill="#D97706">भारत</text>
            </svg>
          </div>
          <div className="pan-gov-right">
            <span>भारत सरकार</span>
            <span className="en">GOVT. OF INDIA</span>
          </div>
        </div>

        <div className="pan-body">
          <div className="pan-left-details">
            <div className="pan-field">
              <div className="pan-k">स्थायी लेखा संख्या / Permanent Account Number</div>
              <div className={`pan-v font-mono font-bold pan-number ${isMismatch ? 'text-danger' : 'text-success'}`}>
                {data?.panNumber || "AABCT2341P"}
              </div>
            </div>

            <div className="pan-field">
              <div className="pan-k">नाम / Name</div>
              <div className="pan-v font-bold">{data?.holderName || "TECHNOVA INFOTECH PRIVATE LIMITED"}</div>
            </div>

            <div className="pan-field">
              <div className="pan-k">निगमन की तारीख / Date of Incorporation</div>
              <div className="pan-v font-mono">{data?.incorporationDate || "12/04/2021"}</div>
            </div>

            <div className="pan-status-tag">
              Status: <span>{data?.panStatus || "Active & Operative"}</span> · Category: <span>{data?.entityType || "Company"}</span>
            </div>
          </div>

          <div className="pan-right-photo">
            <div className="pan-hologram">
              <div className="holo-sheen"></div>
              <span>GOI ITD</span>
            </div>
            <div className="pan-sign-placeholder">
              <span>Digitally Signed</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// 3. Udyam MSME Registration Certificate
function UdyamTemplate({ data }) {
  return (
    <div className="doc-content doc-udyam-theme">
      <div className="udyam-header">
        <div className="udyam-logo-row">
          <div className="udyam-seal">🇮🇳 सूक्ष्म, लघु एवं मध्यम उद्यम</div>
          <div className="udyam-title-center">
            <h3>MINISTRY OF MICRO, SMALL & MEDIUM ENTERPRISES</h3>
            <h2>UDYAM REGISTRATION CERTIFICATE</h2>
          </div>
          <div className="udyam-seal-right">UDYAM</div>
        </div>
      </div>

      <div className="doc-divider"></div>

      <div className="udyam-body">
        <div className="udyam-row">
          <span className="label">UDYAM REGISTRATION NUMBER</span>
          <span className="val font-mono font-bold text-success">{data?.udyamNumber || "UDYAM-MH-01-0024891"}</span>
        </div>
        <div className="udyam-row">
          <span className="label">NAME OF ENTERPRISE</span>
          <span className="val font-bold">{data?.enterpriseName || "M/S TECHNOVA INFOTECH PRIVATE LIMITED"}</span>
        </div>
        <div className="udyam-row">
          <span className="label">TYPE OF ENTERPRISE</span>
          <span className="val highlight-pill">{data?.typeOfEnterprise || "Micro"} Enterprise</span>
        </div>
        <div className="udyam-row">
          <span className="label">MAJOR ACTIVITY</span>
          <span className="val">{data?.majorActivity || "Services (IT & Cloud Architecture)"}</span>
        </div>
        <div className="udyam-row">
          <span className="label">DATE OF INCORPORATION</span>
          <span className="val font-mono">{data?.dateOfIncorporation || "12/04/2021"}</span>
        </div>
        <div className="udyam-row">
          <span className="label">NATIONAL INDUSTRY CLASSIFICATION (NIC)</span>
          <span className="val">{data?.nicCode || "62020 - Computer consultancy"}</span>
        </div>
      </div>

      <div className="udyam-footer">
        <div className="benefits-note">
          ✓ Verified for Public Procurement Policy: 100% EMD Exemption & Purchase Preference Eligible
        </div>
      </div>
    </div>
  );
}

// 4. Startup India Certificate of Recognition
function StartupTemplate({ data, isFlagged, isMissing }) {
  if (isMissing) {
    return (
      <div className="doc-content doc-missing-state">
        <div className="missing-notice">
          <div className="missing-icon">🚫</div>
          <h3>Document Not Submitted</h3>
          <p>The vendor did not provide a Startup India (DPIIT) Certificate.</p>
          <div className="rule-impact">
            <strong>Impact on Tender:</strong> Vendor is not eligible for turnover & prior experience exemption under GFR Rule 173(i). Minimum ₹5 Crore audited turnover rule will apply.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="doc-content doc-startup-theme">
      <div className="startup-header">
        <div className="startup-logo">
          <span className="badge-flag">#startupindia</span>
          <span className="sub">DEPARTMENT FOR PROMOTION OF INDUSTRY AND INTERNAL TRADE</span>
        </div>
        <h2 className="cert-main">CERTIFICATE OF RECOGNITION</h2>
      </div>

      <div className="doc-divider"></div>

      <div className="startup-body">
        <p className="cert-para">
          This is to certify that <strong>{data?.startupName || "TECHNOVA INFOTECH PRIVATE LIMITED"}</strong> is recognized as a startup by the Department for Promotion of Industry and Internal Trade (DPIIT).
        </p>

        <div className="startup-meta-card">
          <div className="meta-item">
            <span className="k">Certificate No:</span>
            <span className="v font-mono font-bold text-success">{data?.dippNumber || "DIPP98412"}</span>
          </div>
          <div className="meta-item">
            <span className="k">Date of Issue:</span>
            <span className="v font-mono">{data?.issueDate || "28/06/2021"}</span>
          </div>
          <div className="meta-item">
            <span className="k">Statutory Validity:</span>
            <span className={`v font-bold ${isFlagged ? 'text-warning' : 'text-success'}`}>
              {data?.validity || "Valid up to 10 years from incorporation (until 11/04/2031)"}
            </span>
          </div>
          <div className="meta-item">
            <span className="k">Industry Sector:</span>
            <span className="v">{data?.industry || "IT Services / Cloud Computing"}</span>
          </div>
        </div>

        {isFlagged && (
          <div className="warning-callout">
            <strong>⚠️ Officer Review Note:</strong> Exemption cutoff is within 60 days. GFR Rule 173(i) exemption is active today but will expire during the execution period.
          </div>
        )}
      </div>

      <div className="startup-footer">
        <div className="stamp-zone">
          <div className="dpiit-seal">DPIIT Govt. of India</div>
          <div className="auth-sign">Authorized Signatory - Startup India</div>
        </div>
      </div>
    </div>
  );
}

// 5. Manufacturer Authorization Form (MAF)
function OemTemplate({ data, isFaintSeal }) {
  return (
    <div className="doc-content doc-oem-theme">
      <div className="oem-letterhead">
        <div className="oem-corp-brand">
          <span className="corp-name">{data?.oemName || "Dell Technologies India Pvt. Ltd."}</span>
          <span className="corp-addr">Level 7, Divyasree Greens, Koramangala, Bengaluru - 560071</span>
        </div>
        <div className="letter-meta font-mono">
          <div>Ref: OEM/GOV-AUTH/2026/894</div>
          <div>Date: {data?.authorizationDate || "05/10/2026"}</div>
        </div>
      </div>

      <div className="doc-divider"></div>

      <div className="oem-body">
        <div className="letter-to">
          <div>To,</div>
          <div>The Tender Inviting Authority,</div>
          <div>Ministry of Electronics & Information Technology (MeitY), New Delhi</div>
        </div>

        <div className="subject-line font-bold">
          Subject: Manufacturer’s Authorization Form (MAF) for Tender Ref: <span className="highlight-pill font-mono">{data?.tenderReference || "GeM/2026/B/89412"}</span>
        </div>

        <p className="letter-body-p">
          Dear Sir/Madam,
        </p>
        <p className="letter-body-p">
          We, <strong>{data?.oemName || "Dell Technologies India Pvt. Ltd."}</strong>, who are established and reputable manufacturers of enterprise server hardware having factories at Sriperumbudur, Tamil Nadu, do hereby authorize:
        </p>

        <div className="authorized-partner-card">
          <div className="partner-title">AUTHORIZED BIDDER / PARTNER</div>
          <div className="partner-name font-bold text-success">{data?.authorizedPartner || "TechNova Infotech Pvt. Ltd."}</div>
          <div className="partner-sub">Authorized to submit bids, negotiate, and provide warranty support for Tender {data?.tenderReference}</div>
        </div>

        <p className="letter-body-p">
          We hereby extend our full manufacturer's warranty, direct replacement support, and cloud backline maintenance through <strong>{data?.validityDate || "31/12/2027"}</strong> as per the terms and conditions of this bid.
        </p>
      </div>

      <div className="oem-footer">
        <div className="signatory-column">
          <div className="sig-name font-bold">{data?.signatory || "Rajesh Krishnamurthy"}</div>
          <div className="sig-desig">Director - Enterprise Public Sector Channels</div>
          <div className="sig-corp">{data?.oemName}</div>
        </div>
        <div className="seal-column">
          <div className={`corporate-rubber-stamp ${isFaintSeal ? 'faint-rubber-seal' : ''}`}>
            <div className="stamp-ring">
              <span className="stamp-text-arc">{data?.oemName?.split(" ")[0] || "DELL"} CORPORATE SEAL</span>
              <span className="stamp-center">GOVT APPROVED</span>
              <span className="stamp-date">OCT 2026</span>
            </div>
            {isFaintSeal && <span className="faint-warning-pill">⚠️ Faint Ink (OCR 64%)</span>}
          </div>
        </div>
      </div>
    </div>
  );
}
