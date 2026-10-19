import uuid
import hashlib
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.app.models.organization import Organization
from backend.app.models.user import User
from backend.app.models.tender import Tender, TenderRequirement
from backend.app.models.vendor import Vendor
from backend.app.models.document import VendorDocument, DocumentVersion
from backend.app.models.analysis import ExtractedField, ComplianceFinding
from backend.app.models.audit import AuditEvent


def seed_database_benchmarks(db: Session) -> None:
    """
    Seeds initial Indian government procurement organization, tender specifications,
    default procurement officer, and 3 complete benchmark vendors matching GeM 4.0 standards.
    Safe for multiple idempotent executions; updates existing vendor dossiers in-place.
    """
    # 1. Organization
    org = db.query(Organization).filter(
        (Organization.id == "org-gem-meity") | (Organization.code == "MeitY-GeM-4.0")
    ).first()
    if not org:
        org = Organization(
            id="org-gem-meity",
            name="Ministry of Electronics & Information Technology (MeitY)",
            code="MeitY-GeM-4.0",
            org_type="GOVERNMENT_DEPARTMENT"
        )
        db.add(org)
        db.flush()

    # 2. RBAC Users (Admin, Procurement Officer, Reviewer, Vendor, Read-only)
    from backend.app.core.security import get_password_hash
    from backend.app.core.roles import UserRole

    rbac_users = [
        ("user-admin-default", "admin@gem.gov.in", "A. Verma (System Admin)", "AdminPassword123!", UserRole.ADMIN.value),
        ("user-officer-default", "officer@gem.gov.in", "S. Sharma (Procurement Officer)", "OfficerPassword123!", UserRole.PROCUREMENT_OFFICER.value),
        ("user-reviewer-default", "reviewer@gem.gov.in", "R. Patel (Technical Reviewer)", "ReviewerPassword123!", UserRole.REVIEWER.value),
        ("user-vendor-default", "vendor@technova.in", "V. Rao (TechNova Representative)", "VendorPassword123!", UserRole.VENDOR.value),
        ("user-auditor-default", "auditor@cag.gov.in", "K. Menon (CAG Statutory Auditor)", "AuditorPassword123!", UserRole.READ_ONLY.value),
    ]

    for uid, uemail, ufname, upass, urole in rbac_users:
        u = db.query(User).filter((User.id == uid) | (User.email == uemail)).first()
        if not u:
            u = User(
                id=uid,
                organization_id=org.id,
                email=uemail,
                full_name=ufname,
                hashed_password=get_password_hash(upass),
                role=urole,
                is_active=True
            )
            db.add(u)
        else:
            u.hashed_password = get_password_hash(upass)
            u.role = urole
        db.flush()

    # 3. Tender
    tender = db.query(Tender).filter(
        (Tender.id == "tender-gem-89412") | (Tender.tender_ref_id == "GeM/2026/B/89412")
    ).first()
    if not tender:
        tender = Tender(
            id="tender-gem-89412",
            organization_id=org.id,
            tender_ref_id="GeM/2026/B/89412",
            title="Supply, Installation & Maintenance of Cloud-Ready Data Center Servers",
            department="Ministry of Electronics & Information Technology (MeitY)",
            portal="Government e-Marketplace (GeM 4.0)",
            minimum_turnover="₹5.00 Crore (Exempted for DPIIT-Recognized Startups & Micro/Small MSMEs)",
            validity_requirement="Documents must be active and valid at least through 2026-11-30",
            submission_deadline=datetime(2026, 10, 18, 17, 0, tzinfo=timezone.utc),
            bid_opening_date=datetime(2026, 10, 25, 10, 0, tzinfo=timezone.utc),
            is_active=True
        )
        db.add(tender)
        db.flush()

        reqs = [
            ("GST_CERTIFICATE", "GST Registration Certificate (Form REG-06)", True, "RULE_GST_ACTIVE"),
            ("PAN_CARD", "Permanent Account Number (PAN Card)", True, "RULE_PAN_GSTIN_MATCH"),
            ("UDYAM_MSME", "Udyam / MSME Registration Certificate", False, "RULE_MSME_EMD_EXEMPTION"),
            ("STARTUP_INDIA", "Startup India DPIIT Recognition Certificate", False, "RULE_STARTUP_VALID"),
            ("OEM_MAF", "Manufacturer / OEM Authorization Form (MAF)", True, "RULE_OEM_TENDER_REF"),
        ]
        for dtype, title, is_mand, rcode in reqs:
            tr = TenderRequirement(
                tender_id=tender.id,
                document_type=dtype,
                title=title,
                is_mandatory=is_mand,
                rule_code=rcode,
                description=f"Mandatory statutory requirement under GeM clause for {title}"
            )
            db.add(tr)
        db.flush()

    # 4. Helper to seed or update a benchmark vendor idempotently
    def _create_benchmark(v_id, name, cin, pan, gstin, status, conf, a_time, summary, docs_spec):
        v = db.query(Vendor).filter(Vendor.id == v_id).first()
        if not v:
            v = Vendor(
                id=v_id,
                organization_id=org.id,
                tender_id=tender.id,
                name=name,
                cin=cin,
                pan=pan,
                gstin=gstin,
                overall_status=status,
                confidence_score=conf,
                audit_time_seconds=a_time,
                summary=summary
            )
            db.add(v)
            db.flush()
        else:
            v.name = name
            v.cin = cin
            v.pan = pan
            v.gstin = gstin
            v.overall_status = status
            v.confidence_score = conf
            v.audit_time_seconds = a_time
            v.summary = summary
            db.flush()

        for doc_info in docs_spec:
            vdoc_id = f"{v_id}-{doc_info['dtype'].lower()}"
            vdoc = db.query(VendorDocument).filter(VendorDocument.id == vdoc_id).first()
            if not vdoc:
                vdoc = VendorDocument(
                    id=vdoc_id,
                    organization_id=org.id,
                    vendor_id=v.id,
                    document_type=doc_info["dtype"],
                    title=doc_info["title"],
                    form_type=doc_info["formType"],
                    status=doc_info["status"]
                )
                db.add(vdoc)
                db.flush()
            else:
                vdoc.document_type = doc_info["dtype"]
                vdoc.title = doc_info["title"]
                vdoc.form_type = doc_info["formType"]
                vdoc.status = doc_info["status"]
                db.flush()

            # Version
            dver = db.query(DocumentVersion).filter(
                DocumentVersion.vendor_document_id == vdoc.id
            ).order_by(DocumentVersion.version_number.desc()).first()
            if not dver:
                dver = DocumentVersion(
                    vendor_document_id=vdoc.id,
                    version_number=1,
                    file_id=str(uuid.uuid4()),
                    file_name=f"{doc_info['dtype'].lower()}.pdf",
                    file_size_bytes=1024 * 50,
                    mime_type="application/pdf",
                    sha256_hash=hashlib.sha256(f"{v_id}-{doc_info['dtype']}".encode("utf-8")).hexdigest(),
                    page_count=1
                )
                db.add(dver)
                db.flush()

            # Fields & Bounding Boxes
            bboxes = list(doc_info.get("boundingBoxes", []))
            assigned_b_ids = set()

            for f_key, f_val in doc_info["extractedData"].items():
                bbox_data = None
                k = f_key.lower()
                for b in bboxes:
                    if b["id"] in assigned_b_ids:
                        continue
                    bid = b.get("id", "").lower()
                    blab = b.get("label", "").lower()
                    if (k in bid or k in blab or 
                        ("gst" in k and "gst" in bid) or 
                        ("pan" in k and "pan" in bid) or 
                        ("name" in k and "name" in bid) or 
                        ("udyam" in k and "udyam" in bid) or 
                        ("dipp" in k and ("dipp" in bid or "startup" in bid)) or 
                        ("tender" in k and "tender" in bid) or 
                        ("seal" in k and "seal" in bid) or 
                        ("sign" in k and "sign" in bid) or 
                        ("valid" in k and "valid" in bid)):
                        bbox_data = b
                        assigned_b_ids.add(b["id"])
                        break

                if not bbox_data:
                    for b in bboxes:
                        if b["id"] not in assigned_b_ids:
                            bbox_data = b
                            assigned_b_ids.add(b["id"])
                            break

                ef = db.query(ExtractedField).filter(
                    ExtractedField.document_version_id == dver.id,
                    ExtractedField.field_key == f_key
                ).first()

                val_status = "VALID" if doc_info["status"] == "COMPLIANT" else ("WARNING" if doc_info["status"] == "REQUIRES_REVIEW" else "INVALID")
                if not ef:
                    ef = ExtractedField(
                        document_version_id=dver.id,
                        field_key=f_key,
                        field_value=str(f_val),
                        normalized_value=str(f_val).upper(),
                        confidence=0.99,
                        page_number=1,
                        bounding_box=bbox_data,
                        validation_status=val_status
                    )
                    db.add(ef)
                else:
                    ef.field_value = str(f_val)
                    ef.normalized_value = str(f_val).upper()
                    ef.bounding_box = bbox_data
                    ef.validation_status = val_status

            # Ensure all remaining bounding boxes are also preserved as ExtractedField entries
            for b in bboxes:
                if b["id"] not in assigned_b_ids:
                    extra_key = f"evidence_{b['id'].replace('box-', '')}"
                    ef_extra = db.query(ExtractedField).filter(
                        ExtractedField.document_version_id == dver.id,
                        ExtractedField.field_key == extra_key
                    ).first()
                    if not ef_extra:
                        ef_extra = ExtractedField(
                            document_version_id=dver.id,
                            field_key=extra_key,
                            field_value=b.get("text", b.get("label", "")),
                            normalized_value=b.get("text", b.get("label", "")).upper(),
                            confidence=0.99,
                            page_number=1,
                            bounding_box=b,
                            validation_status="VALID" if b.get("status") == "valid" else ("WARNING" if b.get("status") == "warning" else "INVALID")
                        )
                        db.add(ef_extra)
                    else:
                        ef_extra.bounding_box = b
                        ef_extra.validation_status = "VALID" if b.get("status") == "valid" else ("WARNING" if b.get("status") == "warning" else "INVALID")

            # Findings
            cf = db.query(ComplianceFinding).filter(
                ComplianceFinding.document_version_id == dver.id
            ).first()
            sev = "CRITICAL" if doc_info["status"] == "NON_COMPLIANT" else ("WARNING" if doc_info["status"] == "REQUIRES_REVIEW" else "INFO")
            if not cf:
                cf = ComplianceFinding(
                    document_version_id=dver.id,
                    rule_code=f"RULE_{doc_info['dtype']}",
                    severity=sev,
                    title=f"{doc_info['title']} Verification",
                    simple_reason=doc_info["evaluation"]["simpleReason"],
                    expected_rule=doc_info["evaluation"]["expectedRule"],
                    confidence=doc_info["evaluation"]["confidence"],
                    status=doc_info["status"],
                    page_number=1
                )
                db.add(cf)
            else:
                cf.rule_code = f"RULE_{doc_info['dtype']}"
                cf.severity = sev
                cf.title = f"{doc_info['title']} Verification"
                cf.simple_reason = doc_info["evaluation"]["simpleReason"]
                cf.expected_rule = doc_info["evaluation"]["expectedRule"]
                cf.confidence = doc_info["evaluation"]["confidence"]
                cf.status = doc_info["status"]

    # =========================================================================
    # 1. TechNova Infotech Pvt. Ltd. (COMPLIANT)
    # =========================================================================
    _create_benchmark(
        v_id="vendor-1",
        name="TechNova Infotech Pvt. Ltd.",
        cin="U72900MH2021PTC359812",
        pan="AABCT2341P",
        gstin="27AABCT2341P1ZB",
        status="COMPLIANT",
        conf=98.4,
        a_time=4.8,
        summary="All 5 statutory and OEM documents are verified valid. The PAN embedded in the GSTIN perfectly matches the standalone PAN card. Entity qualifies for MSME price preference under Udyam Micro Enterprise category.",
        docs_spec=[
            {
                "dtype": "GST_CERTIFICATE",
                "title": "GST Registration Certificate",
                "formType": "Form REG-06",
                "status": "COMPLIANT",
                "extractedData": {
                    "gstin": "27AABCT2341P1ZB",
                    "legalName": "TechNova Infotech Private Limited",
                    "tradeName": "TechNova Cloud Solutions",
                    "registrationDate": "15/04/2021",
                    "validityPeriod": "From 15/04/2021 to Unlimited (Regular)",
                    "constitutionOfBusiness": "Private Limited Company",
                    "principalPlace": "Plot 42, MIDC Industrial Area, Andheri East, Mumbai 400093",
                    "stateCode": "27 (Maharashtra)"
                },
                "evaluation": {
                    "status": "COMPLIANT",
                    "simpleReason": "Active regular GSTIN verified. The certificate has no expiry date (unlimited regular status) and is verified active on the GST portal.",
                    "expectedRule": "Active GST status as of tender deadline (18 Oct 2026)",
                    "confidence": "99.4%"
                },
                "boundingBoxes": [
                    {"id": "box-gst-num", "label": "GSTIN Number", "x": 28.0, "y": 15.5, "width": 44.0, "height": 4.8, "status": "valid", "text": "GSTIN: 27AABCT2341P1ZB"},
                    {"id": "box-gst-name", "label": "Legal Entity Name", "x": 28.0, "y": 22.0, "width": 55.0, "height": 4.5, "status": "valid", "text": "Legal Name: TechNova Infotech Private Limited"},
                    {"id": "box-gst-valid", "label": "Validity Status", "x": 28.0, "y": 39.0, "width": 48.0, "height": 4.5, "status": "valid", "text": "Period of Validity: From 15/04/2021 to Unlimited"},
                    {"id": "box-gst-sign", "label": "Digital Signature / QR", "x": 62.0, "y": 78.0, "width": 28.0, "height": 14.0, "status": "valid", "text": "Digitally signed by GST Superintendent"}
                ]
            },
            {
                "dtype": "PAN_CARD",
                "title": "Permanent Account Number (PAN)",
                "formType": "Income Tax Department (Form 49A)",
                "status": "COMPLIANT",
                "extractedData": {
                    "panNumber": "AABCT2341P",
                    "holderName": "TECHNOVA INFOTECH PRIVATE LIMITED",
                    "incorporationDate": "12/04/2021",
                    "entityType": "Company (Character 4 = 'C')",
                    "panStatus": "Operative & Active"
                },
                "evaluation": {
                    "status": "COMPLIANT",
                    "simpleReason": "PAN number AABCT2341P precisely matches digits 3 to 12 of the submitted GSTIN (27-AABCT2341P-1ZB). Company name spelling matches 100%.",
                    "expectedRule": "PAN must match GSTIN characters 3-12 and legal name",
                    "confidence": "99.8%"
                },
                "boundingBoxes": [
                    {"id": "box-pan-num", "label": "Permanent Account Number", "x": 25.0, "y": 62.0, "width": 50.0, "height": 7.0, "status": "valid", "text": "PAN: AABCT2341P"},
                    {"id": "box-pan-name", "label": "Company Name", "x": 18.0, "y": 44.0, "width": 64.0, "height": 6.0, "status": "valid", "text": "TECHNOVA INFOTECH PRIVATE LIMITED"},
                    {"id": "box-pan-dob", "label": "Date of Incorporation", "x": 18.0, "y": 52.0, "width": 40.0, "height": 5.0, "status": "valid", "text": "12/04/2021"}
                ]
            },
            {
                "dtype": "UDYAM_MSME",
                "title": "Udyam MSME Registration Certificate",
                "formType": "Ministry of MSME, Govt of India",
                "status": "COMPLIANT",
                "extractedData": {
                    "udyamNumber": "UDYAM-MH-01-0024891",
                    "enterpriseName": "M/S TECHNOVA INFOTECH PRIVATE LIMITED",
                    "typeOfEnterprise": "Micro",
                    "majorActivity": "Services (IT & Cloud Architecture)",
                    "dateOfIncorporation": "12/04/2021",
                    "nicCode": "62020 - Computer consultancy and computer facilities management"
                },
                "evaluation": {
                    "status": "COMPLIANT",
                    "simpleReason": "Valid active Udyam registration. As a registered Micro Enterprise, bidder is entitled to 100% Earnest Money Deposit (EMD) exemption and 15% price purchase preference.",
                    "expectedRule": "Valid MSME certificate for tender fee and EMD exemption",
                    "confidence": "97.8%"
                },
                "boundingBoxes": [
                    {"id": "box-udyam-num", "label": "Udyam Registration No.", "x": 24.0, "y": 22.0, "width": 52.0, "height": 5.0, "status": "valid", "text": "UDYAM-MH-01-0024891"},
                    {"id": "box-udyam-cat", "label": "Classification", "x": 24.0, "y": 38.0, "width": 35.0, "height": 5.0, "status": "valid", "text": "Type of Enterprise: Micro"},
                    {"id": "box-udyam-name", "label": "Enterprise Name", "x": 24.0, "y": 30.0, "width": 52.0, "height": 5.0, "status": "valid", "text": "TECHNOVA INFOTECH PRIVATE LIMITED"}
                ]
            },
            {
                "dtype": "STARTUP_INDIA",
                "title": "Startup India Certificate of Recognition",
                "formType": "DPIIT, Ministry of Commerce & Industry",
                "status": "COMPLIANT",
                "extractedData": {
                    "dippNumber": "DIPP98412",
                    "startupName": "TECHNOVA INFOTECH PRIVATE LIMITED",
                    "issueDate": "28/06/2021",
                    "validity": "Valid up to 10 years from incorporation (until 11/04/2031)",
                    "industry": "IT Services / Cloud Computing"
                },
                "evaluation": {
                    "status": "COMPLIANT",
                    "simpleReason": "Entity recognized by DPIIT within valid 10-year statutory window. Qualifies for exemption from prior turnover and experience under GFR Rule 173(i).",
                    "expectedRule": "DPIIT recognition within 10 years of incorporation",
                    "confidence": "98.9%"
                },
                "boundingBoxes": [
                    {"id": "box-dipp-num", "label": "Recognition Number", "x": 26.0, "y": 32.0, "width": 48.0, "height": 5.5, "status": "valid", "text": "Certificate No: DIPP98412"},
                    {"id": "box-dipp-date", "label": "Date of Issue & Period", "x": 26.0, "y": 55.0, "width": 50.0, "height": 5.0, "status": "valid", "text": "Valid until 11/04/2031"}
                ]
            },
            {
                "dtype": "OEM_MAF",
                "title": "Manufacturer Authorization Form (MAF)",
                "formType": "OEM Tender Authorization",
                "status": "COMPLIANT",
                "extractedData": {
                    "oemName": "Dell Technologies India Pvt. Ltd.",
                    "authorizedPartner": "TechNova Infotech Pvt. Ltd.",
                    "tenderReference": "GeM/2026/B/89412",
                    "authorizationDate": "05/10/2026",
                    "validityDate": "31/12/2027",
                    "signatory": "Rajesh Krishnamurthy, Director - Enterprise Channels",
                    "officialSealPresent": True
                },
                "evaluation": {
                    "status": "COMPLIANT",
                    "simpleReason": "OEM letter explicitly quotes this tender ID (GeM/2026/B/89412), valid through Dec 2027, and contains verified OEM executive signature and corporate seal.",
                    "expectedRule": "Tender-specific MAF with official signature and seal",
                    "confidence": "96.5%"
                },
                "boundingBoxes": [
                    {"id": "box-oem-ref", "label": "Tender Reference", "x": 20.0, "y": 32.0, "width": 60.0, "height": 5.5, "status": "valid", "text": "Tender Ref: GeM/2026/B/89412"},
                    {"id": "box-oem-partner", "label": "Authorized Partner", "x": 20.0, "y": 40.0, "width": 60.0, "height": 5.5, "status": "valid", "text": "Partner: TechNova Infotech Pvt. Ltd."},
                    {"id": "box-oem-seal", "label": "Signatory & Corporate Seal", "x": 55.0, "y": 72.0, "width": 35.0, "height": 18.0, "status": "valid", "text": "Dell Technologies Official Seal & Sign"}
                ]
            }
        ]
    )

    # =========================================================================
    # 2. Apex Global Systems Ltd. (NON_COMPLIANT)
    # =========================================================================
    _create_benchmark(
        v_id="vendor-2",
        name="Apex Global Systems Ltd.",
        cin="U74999DL2018PLC339412",
        pan="BBACA9921K",
        gstin="07AAACA9921K1ZN",
        status="NON_COMPLIANT",
        conf=94.2,
        a_time=3.9,
        summary="CRITICAL NON-COMPLIANCE: Immediate disqualification recommended. Entity submitted a cancelled GST certificate from 2024 and the standalone PAN card does not match the company identity on the GST filing.",
        docs_spec=[
            {
                "dtype": "GST_CERTIFICATE",
                "title": "GST Registration Certificate",
                "formType": "Form REG-06",
                "status": "NON_COMPLIANT",
                "extractedData": {
                    "gstin": "07AAACA9921K1ZN",
                    "legalName": "Apex Systems & Services LLP",
                    "tradeName": "Apex Global",
                    "registrationDate": "10/02/2018",
                    "validityPeriod": "Cancelled w.e.f. 14/01/2024",
                    "constitutionOfBusiness": "Limited Liability Partnership",
                    "principalPlace": "12 Barakhamba Road, Connaught Place, New Delhi 110001",
                    "stateCode": "07 (Delhi)"
                },
                "evaluation": {
                    "status": "NON_COMPLIANT",
                    "simpleReason": "REJECTED: The GST certificate shows 'Validity: Cancelled w.e.f. 14/01/2024'. Active GST registration through at least Nov 2026 is required for government tenders.",
                    "expectedRule": "Active validity through at least 30/11/2026",
                    "confidence": "99.1%"
                },
                "boundingBoxes": [
                    {"id": "box-gst-num", "label": "GSTIN Number", "x": 28.0, "y": 15.5, "width": 44.0, "height": 4.8, "status": "valid", "text": "GSTIN: 07AAACA9921K1ZN"},
                    {"id": "box-gst-name", "label": "Entity Name Mismatch", "x": 28.0, "y": 22.0, "width": 55.0, "height": 4.5, "status": "invalid", "text": "Apex Systems & Services LLP (Differs from Bidder)"},
                    {"id": "box-gst-valid", "label": "CANCELLED Validity Date", "x": 28.0, "y": 39.0, "width": 48.0, "height": 5.5, "status": "invalid", "text": "Status: Cancelled w.e.f. 14/01/2024"},
                    {"id": "box-gst-sign", "label": "Digital Signature", "x": 62.0, "y": 78.0, "width": 28.0, "height": 14.0, "status": "valid", "text": "Signed 2018"}
                ]
            },
            {
                "dtype": "PAN_CARD",
                "title": "Permanent Account Number (PAN)",
                "formType": "Income Tax Department (Form 49A)",
                "status": "NON_COMPLIANT",
                "extractedData": {
                    "panNumber": "BBACA9921K",
                    "holderName": "APEX GLOBAL SYSTEMS LIMITED",
                    "incorporationDate": "05/06/2018",
                    "entityType": "Public Limited (Character 4 = 'C' / 'L')",
                    "panStatus": "Active"
                },
                "evaluation": {
                    "status": "NON_COMPLIANT",
                    "simpleReason": "REJECTED: Severe Identity Mismatch. Standalone PAN card is BBACA9921K, but the submitted GSTIN embeds AAACA9921K. First letter of PAN differs ('B' vs 'A').",
                    "expectedRule": "PAN must match digits 3-12 of GSTIN",
                    "confidence": "99.9%"
                },
                "boundingBoxes": [
                    {"id": "box-pan-num", "label": "Mismatched PAN Number", "x": 25.0, "y": 62.0, "width": 50.0, "height": 7.0, "status": "invalid", "text": "PAN: BBACA9921K (GST has AAACA9921K)"},
                    {"id": "box-pan-name", "label": "Name on PAN", "x": 18.0, "y": 44.0, "width": 64.0, "height": 6.0, "status": "valid", "text": "APEX GLOBAL SYSTEMS LIMITED"},
                    {"id": "box-pan-dob", "label": "Incorporation Date", "x": 18.0, "y": 52.0, "width": 40.0, "height": 5.0, "status": "valid", "text": "05/06/2018"}
                ]
            },
            {
                "dtype": "UDYAM_MSME",
                "title": "Udyam MSME Registration Certificate",
                "formType": "Ministry of MSME, Govt of India",
                "status": "COMPLIANT",
                "extractedData": {
                    "udyamNumber": "UDYAM-DL-02-0055190",
                    "enterpriseName": "APEX GLOBAL SYSTEMS LIMITED",
                    "typeOfEnterprise": "Small",
                    "majorActivity": "Manufacturing & Assembly",
                    "dateOfIncorporation": "05/06/2018",
                    "nicCode": "26201 - Manufacture of computers"
                },
                "evaluation": {
                    "status": "COMPLIANT",
                    "simpleReason": "Udyam registration is technically active for Small enterprise, but cannot be processed due to primary GST/PAN legal disqualification.",
                    "expectedRule": "Active MSME registration",
                    "confidence": "95.2%"
                },
                "boundingBoxes": [
                    {"id": "box-udyam-num", "label": "Udyam Registration No.", "x": 24.0, "y": 22.0, "width": 52.0, "height": 5.0, "status": "valid", "text": "UDYAM-DL-02-0055190"},
                    {"id": "box-udyam-cat", "label": "Classification", "x": 24.0, "y": 38.0, "width": 35.0, "height": 5.0, "status": "valid", "text": "Type of Enterprise: Small"},
                    {"id": "box-udyam-name", "label": "Enterprise Name", "x": 24.0, "y": 30.0, "width": 52.0, "height": 5.0, "status": "valid", "text": "APEX GLOBAL SYSTEMS LIMITED"}
                ]
            },
            {
                "dtype": "STARTUP_INDIA",
                "title": "Startup India Certificate",
                "formType": "DPIIT",
                "status": "NON_COMPLIANT",
                "extractedData": {
                    "dippNumber": "NOT PROVIDED",
                    "startupName": "N/A",
                    "issueDate": "N/A",
                    "validity": "Not Claimed",
                    "industry": "N/A"
                },
                "evaluation": {
                    "status": "NON_COMPLIANT",
                    "simpleReason": "Startup India certificate was not submitted. Vendor is not exempt from the ₹5 Crore turnover requirement.",
                    "expectedRule": "DPIIT certificate required if claiming turnover exemption",
                    "confidence": "100%"
                },
                "boundingBoxes": []
            },
            {
                "dtype": "OEM_MAF",
                "title": "Manufacturer Authorization Form (MAF)",
                "formType": "OEM Tender Authorization",
                "status": "COMPLIANT",
                "extractedData": {
                    "oemName": "Hewlett Packard Enterprise (HPE) India",
                    "authorizedPartner": "Apex Global Systems Ltd.",
                    "tenderReference": "GeM/2026/B/89412",
                    "authorizationDate": "12/10/2026",
                    "validityDate": "30/11/2027",
                    "signatory": "Vikram Malhotra, Head - Public Sector",
                    "officialSealPresent": True
                },
                "evaluation": {
                    "status": "COMPLIANT",
                    "simpleReason": "OEM authorization is authentic and valid, but vendor overall remains disqualified due to statutory GST failure.",
                    "expectedRule": "Tender-specific MAF with official signature",
                    "confidence": "97.1%"
                },
                "boundingBoxes": [
                    {"id": "box-oem-ref", "label": "Tender Reference", "x": 20.0, "y": 32.0, "width": 60.0, "height": 5.5, "status": "valid", "text": "Tender Ref: GeM/2026/B/89412"},
                    {"id": "box-oem-partner", "label": "Authorized Partner", "x": 20.0, "y": 40.0, "width": 60.0, "height": 5.5, "status": "valid", "text": "Partner: Apex Global Systems Ltd."},
                    {"id": "box-oem-seal", "label": "Signatory & Corporate Seal", "x": 55.0, "y": 72.0, "width": 35.0, "height": 18.0, "status": "valid", "text": "HPE Public Sector Seal"}
                ]
            }
        ]
    )

    # =========================================================================
    # 3. Bharat Cloud Dynamics LLP (REQUIRES_REVIEW)
    # =========================================================================
    _create_benchmark(
        v_id="vendor-3",
        name="Bharat Cloud Dynamics LLP",
        cin="AAS-9418",
        pan="AALFB8124Q",
        gstin="29AALFB8124Q1ZP",
        status="REQUIRES_REVIEW",
        conf=82.5,
        a_time=4.1,
        summary="REQUIRES OFFICER SIGN-OFF: The AI verified all primary identity numbers, but flagged a faint OEM seal and an impending 10-year startup transition. Handed off to human reviewer to prevent false disqualification.",
        docs_spec=[
            {
                "dtype": "GST_CERTIFICATE",
                "title": "GST Registration Certificate",
                "formType": "Form REG-06",
                "status": "COMPLIANT",
                "extractedData": {
                    "gstin": "29AALFB8124Q1ZP",
                    "legalName": "Bharat Cloud Dynamics LLP",
                    "tradeName": "BharatCloud",
                    "registrationDate": "18/12/2016",
                    "validityPeriod": "From 18/12/2016 to Unlimited",
                    "constitutionOfBusiness": "Limited Liability Partnership",
                    "principalPlace": "Outer Ring Road, Bellandur, Bengaluru 560103",
                    "stateCode": "29 (Karnataka)"
                },
                "evaluation": {
                    "status": "COMPLIANT",
                    "simpleReason": "Active GST status confirmed. Registration is unlimited and properly located in Karnataka state.",
                    "expectedRule": "Active GST registration",
                    "confidence": "99.0%"
                },
                "boundingBoxes": [
                    {"id": "box-gst-num", "label": "GSTIN Number", "x": 28.0, "y": 15.5, "width": 44.0, "height": 4.8, "status": "valid", "text": "GSTIN: 29AALFB8124Q1ZP"},
                    {"id": "box-gst-name", "label": "Legal Entity Name", "x": 28.0, "y": 22.0, "width": 55.0, "height": 4.5, "status": "valid", "text": "Bharat Cloud Dynamics LLP"},
                    {"id": "box-gst-valid", "label": "Validity Status", "x": 28.0, "y": 39.0, "width": 48.0, "height": 4.5, "status": "valid", "text": "Period of Validity: Unlimited"},
                    {"id": "box-gst-sign", "label": "Digital Signature", "x": 62.0, "y": 78.0, "width": 28.0, "height": 14.0, "status": "valid", "text": "Signed & Verified"}
                ]
            },
            {
                "dtype": "PAN_CARD",
                "title": "Permanent Account Number (PAN)",
                "formType": "Income Tax Department",
                "status": "COMPLIANT",
                "extractedData": {
                    "panNumber": "AALFB8124Q",
                    "holderName": "BHARAT CLOUD DYNAMICS LLP",
                    "incorporationDate": "15/12/2016",
                    "entityType": "LLP (Character 4 = 'L' / 'F')",
                    "panStatus": "Active"
                },
                "evaluation": {
                    "status": "COMPLIANT",
                    "simpleReason": "PAN matches GSTIN characters 3-12 perfectly (AALFB8124Q). Legal name matches.",
                    "expectedRule": "PAN matches GSTIN",
                    "confidence": "99.6%"
                },
                "boundingBoxes": [
                    {"id": "box-pan-num", "label": "Permanent Account Number", "x": 25.0, "y": 62.0, "width": 50.0, "height": 7.0, "status": "valid", "text": "PAN: AALFB8124Q"},
                    {"id": "box-pan-name", "label": "LLP Name", "x": 18.0, "y": 44.0, "width": 64.0, "height": 6.0, "status": "valid", "text": "BHARAT CLOUD DYNAMICS LLP"},
                    {"id": "box-pan-dob", "label": "Date of Incorporation", "x": 18.0, "y": 52.0, "width": 40.0, "height": 5.0, "status": "valid", "text": "15/12/2016"}
                ]
            },
            {
                "dtype": "UDYAM_MSME",
                "title": "Udyam MSME Registration Certificate",
                "formType": "Ministry of MSME, Govt of India",
                "status": "COMPLIANT",
                "extractedData": {
                    "udyamNumber": "UDYAM-KR-03-0081920",
                    "enterpriseName": "BHARAT CLOUD DYNAMICS LLP",
                    "typeOfEnterprise": "Small",
                    "majorActivity": "IT Cloud Infrastructure",
                    "dateOfIncorporation": "15/12/2016",
                    "nicCode": "62011 - Software and Cloud infrastructure"
                },
                "evaluation": {
                    "status": "COMPLIANT",
                    "simpleReason": "Active Small Enterprise Udyam certificate. Entitled to tender documentation fee exemption.",
                    "expectedRule": "Active MSME registration",
                    "confidence": "98.1%"
                },
                "boundingBoxes": [
                    {"id": "box-udyam-num", "label": "Udyam Registration No.", "x": 24.0, "y": 22.0, "width": 52.0, "height": 5.0, "status": "valid", "text": "UDYAM-KR-03-0081920"},
                    {"id": "box-udyam-cat", "label": "Classification", "x": 24.0, "y": 38.0, "width": 35.0, "height": 5.0, "status": "valid", "text": "Type of Enterprise: Small"},
                    {"id": "box-udyam-name", "label": "Enterprise Name", "x": 24.0, "y": 30.0, "width": 52.0, "height": 5.0, "status": "valid", "text": "BHARAT CLOUD DYNAMICS LLP"}
                ]
            },
            {
                "dtype": "STARTUP_INDIA",
                "title": "Startup India Certificate",
                "formType": "DPIIT",
                "status": "REQUIRES_REVIEW",
                "extractedData": {
                    "dippNumber": "DIPP41920",
                    "startupName": "BHARAT CLOUD DYNAMICS LLP",
                    "issueDate": "20/01/2017",
                    "validity": "Valid until 14/12/2026 (Under 2 months remaining!)",
                    "industry": "Cloud & AI Services"
                },
                "evaluation": {
                    "status": "REQUIRES_REVIEW",
                    "simpleReason": "ATTENTION NEEDED: The 10-year DPIIT startup exemption ends on 14/12/2026. The bidder is valid today, but their exemption expires midway through the procurement period. Review officer must decide whether to request an audited balance sheet.",
                    "expectedRule": "Startup recognition valid throughout tender evaluation",
                    "confidence": "88.2%"
                },
                "boundingBoxes": [
                    {"id": "box-dipp-num", "label": "DPIIT Recognition No.", "x": 26.0, "y": 32.0, "width": 48.0, "height": 5.5, "status": "valid", "text": "Certificate No: DIPP41920"},
                    {"id": "box-dipp-date", "label": "Near-Expiry Validity", "x": 26.0, "y": 55.0, "width": 50.0, "height": 5.0, "status": "warning", "text": "Expires: 14/12/2026 (< 60 days)"}
                ]
            },
            {
                "dtype": "OEM_MAF",
                "title": "Manufacturer Authorization Form (MAF)",
                "formType": "OEM Tender Authorization",
                "status": "REQUIRES_REVIEW",
                "extractedData": {
                    "oemName": "Cisco Systems India Pvt. Ltd.",
                    "authorizedPartner": "Bharat Cloud Dynamics LLP",
                    "tenderReference": "GeM/2026/B/89412",
                    "authorizationDate": "14/10/2026",
                    "validityDate": "31/12/2027",
                    "signatory": "Anand R., Regional Partner Manager",
                    "officialSealPresent": False
                },
                "evaluation": {
                    "status": "REQUIRES_REVIEW",
                    "simpleReason": "ATTENTION NEEDED: Tender ref is correct, but the official rubber stamp is faint and slightly blurred. OCR confidence is 64%. Review officer should click 'Inspect Document' to confirm the physical stamp manually.",
                    "expectedRule": "Legible OEM seal and authorized signatory designation",
                    "confidence": "74.0%"
                },
                "boundingBoxes": [
                    {"id": "box-oem-ref", "label": "Tender Reference", "x": 20.0, "y": 32.0, "width": 60.0, "height": 5.5, "status": "valid", "text": "Tender Ref: GeM/2026/B/89412"},
                    {"id": "box-oem-partner", "label": "Authorized Partner", "x": 20.0, "y": 40.0, "width": 60.0, "height": 5.5, "status": "valid", "text": "Partner: Bharat Cloud Dynamics LLP"},
                    {"id": "box-oem-seal", "label": "Faint Stamp / Unclear Seal", "x": 55.0, "y": 70.0, "width": 35.0, "height": 19.0, "status": "warning", "text": "Faint Rubber Seal (OCR: 64% - Needs human eyes)"}
                ]
            }
        ]
    )

    db.commit()
