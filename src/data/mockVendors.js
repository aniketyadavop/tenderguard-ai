// Mock vendor dossiers for TenderGuard AI - Government Procurement Vendor Compliance
// Reflects authentic Indian Government Procurement (GeM / CPPP) rules and standards.

export const TENDER_DETAILS = {
  tenderId: "GeM/2026/B/89412",
  title: "Supply, Installation & Maintenance of Cloud-Ready Data Center Servers",
  department: "Ministry of Electronics & Information Technology (MeitY)",
  portal: "Government e-Marketplace (GeM 4.0)",
  bidOpeningDate: "2026-10-25",
  submissionDeadline: "2026-10-18 17:00 IST",
  minimumTurnover: "₹5.00 Crore (Exempted for DPIIT-Recognized Startups & Micro/Small MSMEs)",
  validityRequirement: "Documents must be active and valid at least through 2026-11-30",
  mandatoryDocuments: [
    "GST Registration Certificate (Form REG-06)",
    "Permanent Account Number (PAN Card)",
    "Udyam / MSME Registration Certificate",
    "Startup India DPIIT Recognition Certificate (Optional for exemption)",
    "Manufacturer / OEM Authorization Form (MAF)"
  ]
};

export const MOCK_VENDORS = [
  {
    id: "vendor-1",
    name: "TechNova Infotech Pvt. Ltd.",
    cin: "U72900MH2021PTC359812",
    pan: "AABCT2341P",
    gstin: "27AABCT2341P1ZB",
    overallStatus: "COMPLIANT", // COMPLIANT | NON_COMPLIANT | REQUIRES_REVIEW
    confidenceScore: 98.4,
    auditTimeSeconds: 4.8,
    disqualificationReasons: [],
    reviewNotes: [],
    summary: "All 5 statutory and OEM documents are verified valid. The PAN embedded in the GSTIN perfectly matches the standalone PAN card. Entity qualifies for MSME price preference under Udyam Micro Enterprise category.",
    documents: [
      {
        id: "doc-gst",
        title: "GST Registration Certificate",
        formType: "Form REG-06",
        status: "COMPLIANT",
        extractedData: {
          gstin: "27AABCT2341P1ZB",
          legalName: "TechNova Infotech Private Limited",
          tradeName: "TechNova Cloud Solutions",
          registrationDate: "15/04/2021",
          validityPeriod: "From 15/04/2021 to Unlimited (Regular)",
          constitutionOfBusiness: "Private Limited Company",
          principalPlace: "Plot 42, MIDC Industrial Area, Andheri East, Mumbai 400093",
          stateCode: "27 (Maharashtra)"
        },
        evaluation: {
          status: "COMPLIANT",
          simpleReason: "Active regular GSTIN verified. The certificate has no expiry date (unlimited regular status) and is verified active on the GST portal.",
          expectedRule: "Active GST status as of tender deadline (18 Oct 2026)",
          confidence: "99.4%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-gst-num", label: "GSTIN Number", x: 28, y: 15.5, width: 44, height: 4.8, status: "valid", text: "GSTIN: 27AABCT2341P1ZB" },
          { id: "box-gst-name", label: "Legal Entity Name", x: 28, y: 22, width: 55, height: 4.5, status: "valid", text: "Legal Name: TechNova Infotech Private Limited" },
          { id: "box-gst-valid", label: "Validity Status", x: 28, y: 39, width: 48, height: 4.5, status: "valid", text: "Period of Validity: From 15/04/2021 to Unlimited" },
          { id: "box-gst-sign", label: "Digital Signature / QR", x: 62, y: 78, width: 28, height: 14, status: "valid", text: "Digitally signed by GST Superintendent" }
        ]
      },
      {
        id: "doc-pan",
        title: "Permanent Account Number (PAN)",
        formType: "Income Tax Department (Form 49A)",
        status: "COMPLIANT",
        extractedData: {
          panNumber: "AABCT2341P",
          holderName: "TECHNOVA INFOTECH PRIVATE LIMITED",
          incorporationDate: "12/04/2021",
          entityType: "Company (Character 4 = 'C')",
          panStatus: "Operative & Active"
        },
        evaluation: {
          status: "COMPLIANT",
          simpleReason: "PAN number AABCT2341P precisely matches digits 3 to 12 of the submitted GSTIN (27-AABCT2341P-1ZB). Company name spelling matches 100%.",
          expectedRule: "PAN must match GSTIN characters 3-12 and legal name",
          confidence: "99.8%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-pan-num", label: "Permanent Account Number", x: 25, y: 62, width: 50, height: 7, status: "valid", text: "PAN: AABCT2341P" },
          { id: "box-pan-name", label: "Company Name", x: 18, y: 44, width: 64, height: 6, status: "valid", text: "TECHNOVA INFOTECH PRIVATE LIMITED" },
          { id: "box-pan-dob", label: "Date of Incorporation", x: 18, y: 52, width: 40, height: 5, status: "valid", text: "12/04/2021" }
        ]
      },
      {
        id: "doc-udyam",
        title: "Udyam MSME Registration Certificate",
        formType: "Ministry of MSME, Govt of India",
        status: "COMPLIANT",
        extractedData: {
          udyamNumber: "UDYAM-MH-01-0024891",
          enterpriseName: "M/S TECHNOVA INFOTECH PRIVATE LIMITED",
          typeOfEnterprise: "Micro",
          majorActivity: "Services (IT & Cloud Architecture)",
          dateOfIncorporation: "12/04/2021",
          nicCode: "62020 - Computer consultancy and computer facilities management"
        },
        evaluation: {
          status: "COMPLIANT",
          simpleReason: "Valid active Udyam registration. As a registered Micro Enterprise, bidder is entitled to 100% Earnest Money Deposit (EMD) exemption and 15% price purchase preference.",
          expectedRule: "Valid MSME certificate for tender fee and EMD exemption",
          confidence: "97.8%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-udyam-num", label: "Udyam Registration No.", x: 24, y: 22, width: 52, height: 5, status: "valid", text: "UDYAM-MH-01-0024891" },
          { id: "box-udyam-cat", label: "Classification", x: 24, y: 38, width: 35, height: 5, status: "valid", text: "Type of Enterprise: Micro" },
          { id: "box-udyam-name", label: "Enterprise Name", x: 24, y: 30, width: 52, height: 5, status: "valid", text: "TECHNOVA INFOTECH PRIVATE LIMITED" }
        ]
      },
      {
        id: "doc-startup",
        title: "Startup India Certificate of Recognition",
        formType: "DPIIT, Ministry of Commerce & Industry",
        status: "COMPLIANT",
        extractedData: {
          dippNumber: "DIPP98412",
          startupName: "TECHNOVA INFOTECH PRIVATE LIMITED",
          issueDate: "28/06/2021",
          validity: "Valid up to 10 years from incorporation (until 11/04/2031)",
          industry: "IT Services / Cloud Computing"
        },
        evaluation: {
          status: "COMPLIANT",
          simpleReason: "Entity recognized by DPIIT within valid 10-year statutory window. Qualifies for exemption from prior turnover and experience under GFR Rule 173(i).",
          expectedRule: "DPIIT recognition within 10 years of incorporation",
          confidence: "98.9%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-dipp-num", label: "Recognition Number", x: 26, y: 32, width: 48, height: 5.5, status: "valid", text: "Certificate No: DIPP98412" },
          { id: "box-dipp-date", label: "Date of Issue & Period", x: 26, y: 55, width: 50, height: 5, status: "valid", text: "Valid until 11/04/2031" }
        ]
      },
      {
        id: "doc-oem",
        title: "Manufacturer Authorization Form (MAF)",
        formType: "OEM Tender Authorization",
        status: "COMPLIANT",
        extractedData: {
          oemName: "Dell Technologies India Pvt. Ltd.",
          authorizedPartner: "TechNova Infotech Pvt. Ltd.",
          tenderReference: "GeM/2026/B/89412",
          authorizationDate: "05/10/2026",
          validityDate: "31/12/2027",
          signatory: "Rajesh Krishnamurthy, Director - Enterprise Channels",
          officialSealPresent: true
        },
        evaluation: {
          status: "COMPLIANT",
          simpleReason: "OEM letter explicitly quotes this tender ID (GeM/2026/B/89412), valid through Dec 2027, and contains verified OEM executive signature and corporate seal.",
          expectedRule: "Tender-specific MAF with official signature and seal",
          confidence: "96.5%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-oem-ref", label: "Tender Reference", x: 20, y: 32, width: 60, height: 5.5, status: "valid", text: "Tender Ref: GeM/2026/B/89412" },
          { id: "box-oem-partner", label: "Authorized Partner", x: 20, y: 40, width: 60, height: 5.5, status: "valid", text: "Partner: TechNova Infotech Pvt. Ltd." },
          { id: "box-oem-seal", label: "Signatory & Corporate Seal", x: 55, y: 72, width: 35, height: 18, status: "valid", text: "Dell Technologies Official Seal & Sign" }
        ]
      }
    ]
  },
  {
    id: "vendor-2",
    name: "Apex Global Systems Ltd.",
    cin: "U74999DL2018PLC339412",
    pan: "BBACA9921K",
    gstin: "07AAACA9921K1ZN",
    overallStatus: "NON_COMPLIANT",
    confidenceScore: 94.2,
    auditTimeSeconds: 3.9,
    disqualificationReasons: [
      {
        document: "GST Registration Certificate",
        code: "ERR_GST_CANCELLED",
        title: "GST Certificate Expired & Cancelled",
        simpleReason: "The vendor's GST registration was cancelled/expired on 14 Jan 2024. Active GST registration is legally mandatory under tender clause 4.2."
      },
      {
        document: "PAN Card vs GSTIN",
        code: "ERR_PAN_MISMATCH",
        title: "PAN Mismatch Between Documents",
        simpleReason: "The PAN card submitted has number 'BBACA9921K', but the GSTIN submitted is '07AAACA9921K1ZN' (which belongs to PAN 'AAACA9921K'). Two different legal entities are mixed together."
      }
    ],
    reviewNotes: [],
    summary: "CRITICAL NON-COMPLIANCE: Immediate disqualification recommended. Entity submitted a cancelled GST certificate from 2024 and the standalone PAN card does not match the company identity on the GST filing.",
    documents: [
      {
        id: "doc-gst",
        title: "GST Registration Certificate",
        formType: "Form REG-06",
        status: "NON_COMPLIANT",
        extractedData: {
          gstin: "07AAACA9921K1ZN",
          legalName: "Apex Systems & Services LLP",
          tradeName: "Apex Global",
          registrationDate: "10/02/2018",
          validityPeriod: "Cancelled w.e.f. 14/01/2024",
          constitutionOfBusiness: "Limited Liability Partnership",
          principalPlace: "12 Barakhamba Road, Connaught Place, New Delhi 110001",
          stateCode: "07 (Delhi)"
        },
        evaluation: {
          status: "NON_COMPLIANT",
          simpleReason: "REJECTED: The GST certificate shows 'Validity: Cancelled w.e.f. 14/01/2024'. Active GST registration through at least Nov 2026 is required for government tenders.",
          expectedRule: "Active validity through at least 30/11/2026",
          confidence: "99.1%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-gst-num", label: "GSTIN Number", x: 28, y: 15.5, width: 44, height: 4.8, status: "valid", text: "GSTIN: 07AAACA9921K1ZN" },
          { id: "box-gst-name", label: "Entity Name Mismatch", x: 28, y: 22, width: 55, height: 4.5, status: "invalid", text: "Apex Systems & Services LLP (Differs from Bidder)" },
          { id: "box-gst-valid", label: "CANCELLED Validity Date", x: 28, y: 39, width: 48, height: 5.5, status: "invalid", text: "Status: Cancelled w.e.f. 14/01/2024" },
          { id: "box-gst-sign", label: "Digital Signature", x: 62, y: 78, width: 28, height: 14, status: "valid", text: "Signed 2018" }
        ]
      },
      {
        id: "doc-pan",
        title: "Permanent Account Number (PAN)",
        formType: "Income Tax Department (Form 49A)",
        status: "NON_COMPLIANT",
        extractedData: {
          panNumber: "BBACA9921K",
          holderName: "APEX GLOBAL SYSTEMS LIMITED",
          incorporationDate: "05/06/2018",
          entityType: "Public Limited (Character 4 = 'C' / 'L')",
          panStatus: "Active"
        },
        evaluation: {
          status: "NON_COMPLIANT",
          simpleReason: "REJECTED: Severe Identity Mismatch. Standalone PAN card is BBACA9921K, but the submitted GSTIN embeds AAACA9921K. First letter of PAN differs ('B' vs 'A').",
          expectedRule: "PAN must match digits 3-12 of GSTIN",
          confidence: "99.9%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-pan-num", label: "Mismatched PAN Number", x: 25, y: 62, width: 50, height: 7, status: "invalid", text: "PAN: BBACA9921K (GST has AAACA9921K)" },
          { id: "box-pan-name", label: "Name on PAN", x: 18, y: 44, width: 64, height: 6, status: "valid", text: "APEX GLOBAL SYSTEMS LIMITED" },
          { id: "box-pan-dob", label: "Incorporation Date", x: 18, y: 52, width: 40, height: 5, status: "valid", text: "05/06/2018" }
        ]
      },
      {
        id: "doc-udyam",
        title: "Udyam MSME Registration Certificate",
        formType: "Ministry of MSME, Govt of India",
        status: "COMPLIANT",
        extractedData: {
          udyamNumber: "UDYAM-DL-02-0055190",
          enterpriseName: "APEX GLOBAL SYSTEMS LIMITED",
          typeOfEnterprise: "Small",
          majorActivity: "Manufacturing & Assembly",
          dateOfIncorporation: "05/06/2018",
          nicCode: "26201 - Manufacture of computers"
        },
        evaluation: {
          status: "COMPLIANT",
          simpleReason: "Udyam registration is technically active for Small enterprise, but cannot be processed due to primary GST/PAN legal disqualification.",
          expectedRule: "Active MSME registration",
          confidence: "95.2%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-udyam-num", label: "Udyam Registration No.", x: 24, y: 22, width: 52, height: 5, status: "valid", text: "UDYAM-DL-02-0055190" },
          { id: "box-udyam-cat", label: "Classification", x: 24, y: 38, width: 35, height: 5, status: "valid", text: "Type of Enterprise: Small" },
          { id: "box-udyam-name", label: "Enterprise Name", x: 24, y: 30, width: 52, height: 5, status: "valid", text: "APEX GLOBAL SYSTEMS LIMITED" }
        ]
      },
      {
        id: "doc-startup",
        title: "Startup India Certificate",
        formType: "DPIIT",
        status: "NON_COMPLIANT",
        extractedData: {
          dippNumber: "NOT PROVIDED",
          startupName: "N/A",
          issueDate: "N/A",
          validity: "Not Claimed",
          industry: "N/A"
        },
        evaluation: {
          status: "NON_COMPLIANT",
          simpleReason: "Startup India certificate was not submitted. Vendor is not exempt from the ₹5 Crore turnover requirement.",
          expectedRule: "DPIIT certificate required if claiming turnover exemption",
          confidence: "100%",
          pageNumber: 1
        },
        boundingBoxes: []
      },
      {
        id: "doc-oem",
        title: "Manufacturer Authorization Form (MAF)",
        formType: "OEM Tender Authorization",
        status: "COMPLIANT",
        extractedData: {
          oemName: "Hewlett Packard Enterprise (HPE) India",
          authorizedPartner: "Apex Global Systems Ltd.",
          tenderReference: "GeM/2026/B/89412",
          authorizationDate: "12/10/2026",
          validityDate: "30/11/2027",
          signatory: "Vikram Malhotra, Head - Public Sector",
          officialSealPresent: true
        },
        evaluation: {
          status: "COMPLIANT",
          simpleReason: "OEM authorization is authentic and valid, but vendor overall remains disqualified due to statutory GST failure.",
          expectedRule: "Tender-specific MAF with official signature",
          confidence: "97.1%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-oem-ref", label: "Tender Reference", x: 20, y: 32, width: 60, height: 5.5, status: "valid", text: "Tender Ref: GeM/2026/B/89412" },
          { id: "box-oem-partner", label: "Authorized Partner", x: 20, y: 40, width: 60, height: 5.5, status: "valid", text: "Partner: Apex Global Systems Ltd." },
          { id: "box-oem-seal", label: "Signatory & Corporate Seal", x: 55, y: 72, width: 35, height: 18, status: "valid", text: "HPE Public Sector Seal" }
        ]
      }
    ]
  },
  {
    id: "vendor-3",
    name: "Bharat Cloud Dynamics LLP",
    cin: "AAS-9418",
    pan: "AALFB8124Q",
    gstin: "29AALFB8124Q1ZP",
    overallStatus: "REQUIRES_REVIEW",
    confidenceScore: 82.5,
    auditTimeSeconds: 4.1,
    disqualificationReasons: [],
    reviewNotes: [
      {
        document: "Manufacturer Authorization Form (MAF)",
        field: "Signatory Seal & Designation",
        simpleReason: "The OEM official seal on page 1 is partially faint and handwritten. OCR confidence was only 64%. The Procurement Officer needs to do a quick 30-second visual check to confirm the authorization before approving."
      },
      {
        document: "Startup India Certificate",
        field: "Exemption Window Cutoff",
        simpleReason: "Company incorporation was 9 years and 10 months ago (limit is 10 years). The DPIIT certificate is legally valid today, but will expire during the 3-year contract period. Review officer must decide whether to seek a turnover guarantee."
      }
    ],
    summary: "REQUIRES OFFICER SIGN-OFF: The AI verified all primary identity numbers, but flagged a faint OEM seal and an impending 10-year startup transition. Handed off to human reviewer to prevent false disqualification.",
    documents: [
      {
        id: "doc-gst",
        title: "GST Registration Certificate",
        formType: "Form REG-06",
        status: "COMPLIANT",
        extractedData: {
          gstin: "29AALFB8124Q1ZP",
          legalName: "Bharat Cloud Dynamics LLP",
          tradeName: "BharatCloud",
          registrationDate: "18/12/2016",
          validityPeriod: "From 18/12/2016 to Unlimited",
          constitutionOfBusiness: "Limited Liability Partnership",
          principalPlace: "Outer Ring Road, Bellandur, Bengaluru 560103",
          stateCode: "29 (Karnataka)"
        },
        evaluation: {
          status: "COMPLIANT",
          simpleReason: "Active GST status confirmed. Registration is unlimited and properly located in Karnataka state.",
          expectedRule: "Active GST registration",
          confidence: "99.0%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-gst-num", label: "GSTIN Number", x: 28, y: 15.5, width: 44, height: 4.8, status: "valid", text: "GSTIN: 29AALFB8124Q1ZP" },
          { id: "box-gst-name", label: "Legal Entity Name", x: 28, y: 22, width: 55, height: 4.5, status: "valid", text: "Bharat Cloud Dynamics LLP" },
          { id: "box-gst-valid", label: "Validity Status", x: 28, y: 39, width: 48, height: 4.5, status: "valid", text: "Period of Validity: Unlimited" },
          { id: "box-gst-sign", label: "Digital Signature", x: 62, y: 78, width: 28, height: 14, status: "valid", text: "Signed & Verified" }
        ]
      },
      {
        id: "doc-pan",
        title: "Permanent Account Number (PAN)",
        formType: "Income Tax Department",
        status: "COMPLIANT",
        extractedData: {
          panNumber: "AALFB8124Q",
          holderName: "BHARAT CLOUD DYNAMICS LLP",
          incorporationDate: "15/12/2016",
          entityType: "LLP (Character 4 = 'L' / 'F')",
          panStatus: "Active"
        },
        evaluation: {
          status: "COMPLIANT",
          simpleReason: "PAN matches GSTIN characters 3-12 perfectly (AALFB8124Q). Legal name matches.",
          expectedRule: "PAN matches GSTIN",
          confidence: "99.6%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-pan-num", label: "Permanent Account Number", x: 25, y: 62, width: 50, height: 7, status: "valid", text: "PAN: AALFB8124Q" },
          { id: "box-pan-name", label: "LLP Name", x: 18, y: 44, width: 64, height: 6, status: "valid", text: "BHARAT CLOUD DYNAMICS LLP" },
          { id: "box-pan-dob", label: "Date of Incorporation", x: 18, y: 52, width: 40, height: 5, status: "valid", text: "15/12/2016" }
        ]
      },
      {
        id: "doc-udyam",
        title: "Udyam MSME Registration Certificate",
        formType: "Ministry of MSME, Govt of India",
        status: "COMPLIANT",
        extractedData: {
          udyamNumber: "UDYAM-KR-03-0081920",
          enterpriseName: "BHARAT CLOUD DYNAMICS LLP",
          typeOfEnterprise: "Small",
          majorActivity: "IT Cloud Infrastructure",
          dateOfIncorporation: "15/12/2016",
          nicCode: "62011 - Software and Cloud infrastructure"
        },
        evaluation: {
          status: "COMPLIANT",
          simpleReason: "Active Small Enterprise Udyam certificate. Entitled to tender documentation fee exemption.",
          expectedRule: "Active MSME registration",
          confidence: "98.1%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-udyam-num", label: "Udyam Registration No.", x: 24, y: 22, width: 52, height: 5, status: "valid", text: "UDYAM-KR-03-0081920" },
          { id: "box-udyam-cat", label: "Classification", x: 24, y: 38, width: 35, height: 5, status: "valid", text: "Type of Enterprise: Small" },
          { id: "box-udyam-name", label: "Enterprise Name", x: 24, y: 30, width: 52, height: 5, status: "valid", text: "BHARAT CLOUD DYNAMICS LLP" }
        ]
      },
      {
        id: "doc-startup",
        title: "Startup India Certificate",
        formType: "DPIIT",
        status: "REQUIRES_REVIEW",
        extractedData: {
          dippNumber: "DIPP41920",
          startupName: "BHARAT CLOUD DYNAMICS LLP",
          issueDate: "20/01/2017",
          validity: "Valid until 14/12/2026 (Under 2 months remaining!)",
          industry: "Cloud & AI Services"
        },
        evaluation: {
          status: "REQUIRES_REVIEW",
          simpleReason: "ATTENTION NEEDED: The 10-year DPIIT startup exemption ends on 14/12/2026. The bidder is valid today, but their exemption expires midway through the procurement period. Review officer must decide whether to request an audited balance sheet.",
          expectedRule: "Startup recognition valid throughout tender evaluation",
          confidence: "88.2%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-dipp-num", label: "DPIIT Recognition No.", x: 26, y: 32, width: 48, height: 5.5, status: "valid", text: "Certificate No: DIPP41920" },
          { id: "box-dipp-date", label: "Near-Expiry Validity", x: 26, y: 55, width: 50, height: 5, status: "warning", text: "Expires: 14/12/2026 (< 60 days)" }
        ]
      },
      {
        id: "doc-oem",
        title: "Manufacturer Authorization Form (MAF)",
        formType: "OEM Tender Authorization",
        status: "REQUIRES_REVIEW",
        extractedData: {
          oemName: "Cisco Systems India Pvt. Ltd.",
          authorizedPartner: "Bharat Cloud Dynamics LLP",
          tenderReference: "GeM/2026/B/89412",
          authorizationDate: "14/10/2026",
          validityDate: "31/12/2027",
          signatory: "Anand R., Regional Partner Manager",
          officialSealPresent: false
        },
        evaluation: {
          status: "REQUIRES_REVIEW",
          simpleReason: "ATTENTION NEEDED: Tender ref is correct, but the official rubber stamp is faint and slightly blurred. OCR confidence is 64%. Review officer should click 'Inspect Document' to confirm the physical stamp manually.",
          expectedRule: "Legible OEM seal and authorized signatory designation",
          confidence: "74.0%",
          pageNumber: 1
        },
        boundingBoxes: [
          { id: "box-oem-ref", label: "Tender Reference", x: 20, y: 32, width: 60, height: 5.5, status: "valid", text: "Tender Ref: GeM/2026/B/89412" },
          { id: "box-oem-partner", label: "Authorized Partner", x: 20, y: 40, width: 60, height: 5.5, status: "valid", text: "Partner: Bharat Cloud Dynamics LLP" },
          { id: "box-oem-seal", label: "Faint Stamp / Unclear Seal", x: 55, y: 70, width: 35, height: 19, status: "warning", text: "Faint Rubber Seal (OCR: 64% - Needs human eyes)" }
        ]
      }
    ]
  }
];

// Pre-upload checklist & common rejection guide in simple English
export const PRE_SUBMISSION_GUIDE = {
  steps: [
    {
      step: 1,
      title: "Check Document Expiry Dates",
      icon: "calendar",
      summary: "Make sure your certificates are active at least through the tender award date (30 Nov 2026).",
      tips: [
        "GST certificate must show 'Active' status (not Cancelled or Suspended).",
        "DPIIT Startup certificate must be within the 10-year incorporation window."
      ]
    },
    {
      step: 2,
      title: "Confirm Your PAN Matches Your GSTIN",
      icon: "credit-card",
      summary: "In India, characters 3 to 12 of your 15-digit GSTIN are your exact PAN number.",
      tips: [
        "Example: If GSTIN is 27-AABCT2341P-1ZB, your PAN card MUST be AABCT2341P.",
        "Ensure the exact company name spelling matches on both cards."
      ]
    },
    {
      step: 3,
      title: "Verify OEM Letter Tender Reference",
      icon: "file-check",
      summary: "Your Manufacturer Authorization Form (MAF) cannot be a generic letter.",
      tips: [
        "The letter must explicitly mention Tender ID: GeM/2026/B/89412.",
        "It must bear an official physical or digital company seal and authorized signatory name."
      ]
    },
    {
      step: 4,
      title: "Scan in Clear Color at 200+ DPI",
      icon: "camera",
      summary: "Avoid blurry phone photos with dark shadows or cropped corners.",
      tips: [
        "Ensure all QR codes, digital signatures, and dates are crisp.",
        "Acceptable formats: PDF, JPG, PNG (maximum 25MB per file)."
      ]
    }
  ],
  rejectionReasons: [
    {
      rank: 1,
      title: "Expired or Cancelled GST Registration",
      percentage: "42% of rejections",
      plainExplanation: "Vendors upload older PDF certificates from when they first registered, but their status on the portal changed or lapsed. Government tenders strictly require real-time active status.",
      howToAvoid: "Check your active status on gst.gov.in before uploading. TenderGuard AI verifies this automatically."
    },
    {
      rank: 2,
      title: "PAN Number Mismatch with GSTIN",
      percentage: "26% of rejections",
      plainExplanation: "Uploading a director's personal PAN card instead of the company PAN, or uploading a sister company's document. Government rules prohibit mixing entities.",
      howToAvoid: "Cross-check characters 3-12 of your GSTIN with Box 1 of your PAN card before submitting."
    },
    {
      rank: 3,
      title: "Generic or Expired OEM Authorization (MAF)",
      percentage: "18% of rejections",
      plainExplanation: "Submitting a blanket partnership certificate instead of a tender-specific authorization with the exact GeM bid number.",
      howToAvoid: "Request your OEM (Dell, HP, Cisco, etc.) to issue a letter citing Tender No. GeM/2026/B/89412."
    },
    {
      rank: 4,
      title: "Illegible / Faint Signatures & Stamps",
      percentage: "9% of rejections",
      plainExplanation: "Scans where the official seal or signature is too smudged to confirm authorization.",
      howToAvoid: "Always upload original digitally-signed PDFs or crisp 300 DPI flatbed scans."
    },
    {
      rank: 5,
      title: "Invalid MSME Turnover Classification",
      percentage: "5% of rejections",
      plainExplanation: "Claiming Micro/Small enterprise EMD exemption while exceeding the statutory turnover ceiling.",
      howToAvoid: "Submit your latest Udyam Registration Certificate downloaded directly from udyamregistration.gov.in."
    }
  ],
  requiredDocumentsList: [
    {
      name: "GST Certificate (Form REG-06)",
      mandatory: true,
      purpose: "Confirms statutory tax compliance and active business registration.",
      rule: "Must be active with no cancellation notice."
    },
    {
      name: "Permanent Account Number (PAN)",
      mandatory: true,
      purpose: "Confirms corporate legal identity with the Income Tax Department.",
      rule: "Must match digits 3-12 of GSTIN."
    },
    {
      name: "Udyam / MSME Certificate",
      mandatory: false,
      purpose: "Grants 100% exemption from Earnest Money Deposit (EMD) & fee preference.",
      rule: "Must be valid for Micro or Small category."
    },
    {
      name: "Startup India Certificate (DPIIT)",
      mandatory: false,
      purpose: "Exemption from prior turnover and experience criteria under GFR Rule 173(i).",
      rule: "Must be within 10 years of incorporation date."
    },
    {
      name: "Manufacturer Authorization Form (MAF)",
      mandatory: true,
      purpose: "Guarantees authentic hardware warranty and manufacturer support.",
      rule: "Must explicitly reference Tender GeM/2026/B/89412 with seal."
    }
  ]
};
