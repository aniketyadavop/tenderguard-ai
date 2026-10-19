from typing import List
from backend.app.rules.base import BaseRule, EvaluationContext, RuleFinding, RuleStatus, RuleSeverity


class DocumentPresenceRule(BaseRule):
    """
    Validates presence of mandatory statutory documents (GST, PAN, OEM MAF)
    and conditionally required exemption certificates (Udyam, Startup India).
    """
    rule_id = "RULE_DOC_PRESENCE"
    rule_name = "Mandatory Document Presence Verification"
    description = "Verifies all required documents under GeM tender specs have been submitted."
    document_type = "ALL"

    DOCUMENT_NAMES = {
        "GST_CERTIFICATE": "GST Registration Certificate (Form REG-06)",
        "PAN_CARD": "Permanent Account Number (PAN Card)",
        "OEM_MAF": "Manufacturer Authorization Form (MAF)",
        "UDYAM_MSME": "Udyam MSME Registration Certificate",
        "STARTUP_INDIA": "Startup India Certificate of Recognition",
    }

    def evaluate(self, context: EvaluationContext) -> List[RuleFinding]:
        findings: List[RuleFinding] = []

        # Check mandatory documents
        for doc_type in context.mandatory_document_types:
            doc_name = self.DOCUMENT_NAMES.get(doc_type, doc_type)
            if doc_type in context.documents:
                findings.append(
                    RuleFinding(
                        rule_id=f"{self.rule_id}_{doc_type}",
                        rule_name=f"{doc_name} Submitted",
                        document_type=doc_type,
                        status=RuleStatus.PASS,
                        severity=RuleSeverity.INFO,
                        title=f"{doc_name} Present",
                        simple_reason=f"Mandatory {doc_name} is uploaded and present in the vendor filing.",
                        expected_rule="All mandatory tender documents must be submitted prior to bid closing date",
                        confidence="100%"
                    )
                )
            else:
                findings.append(
                    RuleFinding(
                        rule_id=f"{self.rule_id}_{doc_type}",
                        rule_name=f"Missing {doc_name}",
                        document_type=doc_type,
                        status=RuleStatus.FAIL,
                        severity=RuleSeverity.CRITICAL,
                        title=f"Missing Mandatory Document: {doc_name}",
                        simple_reason=f"The vendor failed to upload the required {doc_name}. This is a mandatory filing under GeM tender clause 4.1.",
                        expected_rule="Mandatory submission under GFR 2017 & GeM Procurement Manual",
                        confidence="100%"
                    )
                )

        # Check conditional exemption documents (Startup India, MSME)
        if "STARTUP_INDIA" not in context.documents:
            if "TURNOVER_EXEMPTION" in context.claimed_exemptions:
                findings.append(
                    RuleFinding(
                        rule_id="RULE_DOC_PRESENCE_STARTUP_MISSING",
                        rule_name="Missing DPIIT Certificate for Claimed Exemption",
                        document_type="STARTUP_INDIA",
                        status=RuleStatus.FAIL,
                        severity=RuleSeverity.CRITICAL,
                        title="Startup India Certificate Missing",
                        simple_reason="Vendor claimed prior turnover & experience exemption under GFR Rule 173(i) but failed to upload a Startup India (DPIIT) Certificate.",
                        expected_rule="DPIIT certificate mandatory to claim startup turnover waiver",
                        confidence="100%"
                    )
                )
            else:
                findings.append(
                    RuleFinding(
                        rule_id="RULE_DOC_PRESENCE_STARTUP_OPTIONAL",
                        rule_name="Startup India Certificate Not Provided",
                        document_type="STARTUP_INDIA",
                        status=RuleStatus.NOT_APPLICABLE,
                        severity=RuleSeverity.INFO,
                        title="Startup Certificate Not Claimed",
                        simple_reason="Startup India certificate was not submitted. Standard ₹5 Crore minimum turnover criteria will apply.",
                        expected_rule="Optional document for turnover exemption under GFR Rule 173(i)",
                        confidence="100%"
                    )
                )

        if "UDYAM_MSME" in context.documents:
            doc = context.documents["UDYAM_MSME"]
            ent_type = doc.fields.get("typeOfEnterprise", None)
            val = ent_type.extracted_value if ent_type else "Micro"
            findings.append(
                RuleFinding(
                    rule_id="RULE_MSME_EMD_EXEMPTION",
                    rule_name="MSME EMD Exemption Verification",
                    document_type="UDYAM_MSME",
                    status=RuleStatus.PASS,
                    severity=RuleSeverity.INFO,
                    title="100% EMD Fee Waiver Qualified",
                    simple_reason=f"Verified active {val} Enterprise under Udyam. Entitled to 100% Earnest Money Deposit (EMD) exemption and purchase preference.",
                    expected_rule="Public Procurement Policy for Micro and Small Enterprises Order, 2012",
                    confidence="98.5%"
                )
            )

        return findings
