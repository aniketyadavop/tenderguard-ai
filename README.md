# TenderGuard AI — Explainable AI Framework for Vendor Compliance Verification in Government Procurement

Built for the **AI4Impact** Hackathon track.

## Problem Statement
Verifying vendor compliance in government procurement (GeM / CPPP) is a notorious bottleneck. Auditing GST certificates, PAN cards, Udyam MSME registrations, Startup India recognitions, and OEM authorization requires manually parsing dozens of unstructured documents. Overlooked details stall tenders, while false disqualifications harm legitimate businesses.

## How TenderGuard AI Solves It
- **Explainable by Design**: Every pass, rejection, or warning is paired with a direct visual bounding box trace on the original source document.
- **Categorized & Human-Friendly**: Zero legal jargon. All decisions are presented in plain English with clear before-submission checklists.
- **Human-in-the-Loop**: Edge cases (faint stamps, approaching statutory cutoff dates) are flagged for procurement officer review rather than automated rejection.
- **Zero-Retention Privacy**: Analyzes documents in ephemeral RAM; nothing is stored or used for model training.

## Local Development
- Application folder: `C:\Users\yanuj\.gemini\antigravity-ide\scratch\tenderguard-ai`
- Dev server running at: `http://127.0.0.1:5173/`

### Running the App:
```bash
cd tenderguard-ai
npm run dev
```

### Pre-loaded Demo Scenarios for Judges:
1. **Scenario 1: TechNova Infotech Pvt. Ltd.** -> Fully Compliant (All 5 verified, qualifies for MSME EMD waiver and DPIIT turnover exemption)
2. **Scenario 2: Apex Global Systems Ltd.** -> Disqualified (Expired GST certificate from 2024 + PAN-GSTIN mismatch)
3. **Scenario 3: Bharat Cloud Dynamics LLP** -> Requires Human Review (Faint OEM seal with 64% OCR confidence + Startup 10-year limit expiring within 60 days)
readme
