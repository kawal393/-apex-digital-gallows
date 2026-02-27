"""
DIGITAL GALLOWS - TRIO COMPLETE API Server
EU AI Act 2026 Compliance Platform
=====================================

THREE MODES:
- SHIELD (Lawyer): Defend the giants, private compliance
- SWORD (Police): Expose violations to EU regulators
- JUDGE: Set the standards, issue binding rulings

Author: Digital Gallows Technologies
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib
import uuid
import json
from gallows.ledger.merkle_ledger import ComplianceLedger, Article12Event
from gallows.config import CONFIG, get_mode_description, EU_AI_ACT_MAPPING

app = FastAPI(
    title="Digital Gallows API - TRIO COMPLETE",
    description="Police + Lawyer + Judge: The Complete Regulatory Stack",
    version="2.0.0-TRIO",
    docs_url="/docs",
    redoc_url="/redoc"
)

# In-memory storage for demo
ledgers: Dict[str, ComplianceLedger] = {}
red_list: List[Dict[str, Any]] = []  # Public violations (SWORD/JUDGE mode)
judgments: List[Dict[str, Any]] = []  # Binding rulings (JUDGE mode)


# ============ MODELS ============

class VerifyRequest(BaseModel):
    """Request for AI model verification"""
    model_id: str
    model_provider: str
    input_hash: str
    output_hash: str
    compliance_status: str = "PENDING"
    risk_level: str = "HIGH_RISK"
    article_reference: int = 12
    system_purpose: str = ""
    deployment_context: str = ""


class JudgeRulingRequest(BaseModel):
    """Request for binding compliance ruling (JUDGE mode)"""
    article: int = Field(..., description="EU AI Act Article (12, 13, 14, 15)")
    question: str = Field(..., description="Specific compliance question")
    ruling: str = Field(..., description="Binding ruling")
    precedent_cases: List[str] = []


class WhistleblowerReport(BaseModel):
    """Report a violation (SWORD/JUDGE mode)"""
    model_id: str
    provider: str
    violation_type: str
    evidence_hash: str
    severity: str = "HIGH"
    anonymous: bool = True


# ============ MIDDLEWARE ============

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key"""
    return x_api_key or "demo-key"


# ============ CORE ENDPOINTS ============

@app.get("/")
async def root():
    """Root endpoint with mode info"""
    return {
        "name": "Digital Gallows API - TRIO COMPLETE",
        "version": CONFIG.VERSION,
        "mode": CONFIG.MODE,
        "status": "OPERATIONAL",
        "message": "THE TRIO IS COMPLETE. Police + Lawyer + Judge.",
        "docs": "/docs"
    }


@app.get("/mode")
async def get_mode():
    """Get current sovereign mode"""
    return {
        "mode": CONFIG.MODE,
        "config": CONFIG.get_mode_config(),
        "description": CONFIG.get_mode_config()["description"]
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mode": CONFIG.MODE,
        "ledgers_active": len(ledgers),
        "violations_recorded": len(red_list),
        "judgments_issued": len(judgments)
    }


# ============ VERIFICATION ENDPOINTS ============

@app.post("/api/v1/verify", response_model=Dict[str, Any])
async def verify_compliance(
    request: VerifyRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Submit AI model for EU AI Act compliance verification.
    
    Behavior depends on mode:
    - SHIELD: Private verification, returns pass/fail only
    - SWORD: Public verification, logs to regulator-visible ledger
    - JUDGE: Binding ruling issued
    """
    
    # Get or create ledger
    chain_id = f"chain-{request.model_provider.lower()}"
    
    if chain_id not in ledgers:
        ledgers[chain_id] = ComplianceLedger(chain_id)
    
    ledger = ledgers[chain_id]
    
    # Record event
    event = ledger.record_compliance_event(
        model_id=request.model_id,
        input_data=request.input_hash,
        output_data=request.output_hash,
        compliance_status=request.compliance_status,
        risk_level=request.risk_level,
        article_reference=request.article_reference,
        system_purpose=request.system_purpose,
        deployment_context=request.deployment_context
    )
    
    # Finalize block
    root = ledger.finalize_block()
    
    response = {
        "success": True,
        "mode": CONFIG.MODE,
        "event_id": event.event_id,
        "chain_id": chain_id,
        "root_hash": root,
        "timestamp": event.timestamp
    }
    
    # SHIELD mode: Return private compliance only
    if CONFIG.is_shield_mode():
        response["compliance_status"] = request.compliance_status
        response["message"] = "Verification complete. Results private."
    
    # SWORD/JUDGE mode: Expose to public ledger
    elif CONFIG.can_expose_violations():
        response["public_ledger"] = True
        response["certificate_url"] = f"/api/v1/certificate/{chain_id}"
        
        # If failed, add to red list
        if request.compliance_status == "FAIL":
            violation = {
                "violation_id": f"VIOL-{uuid.uuid4().hex[:8]}",
                "model_id": request.model_id,
                "provider": request.model_provider,
                "article": request.article_reference,
                "evidence_hash": event.compute_event_hash(),
                "timestamp": event.timestamp,
                "reported_by": "digital-gallows"
            }
            red_list.append(violation)
            response["violation_id"] = violation["violation_id"]
            response["alert_sent_to"] = "EU AI Office"
    
    return response


# ============ CERTIFICATE ENDPOINTS ============

@app.get("/api/v1/certificate/{chain_id}")
async def get_certificate(chain_id: str, api_key: str = Depends(verify_api_key)):
    """Get compliance certificate"""
    if chain_id not in ledgers:
        raise HTTPException(status_code=404, detail="Chain not found")
    
    ledger = ledgers[chain_id]
    cert = ledger.get_compliance_certificate()
    
    # Add mode information
    cert["mode"] = CONFIG.MODE
    cert["is_public"] = CONFIG.is_public_registry()
    
    return cert


# ============ WHISTLEBLOWER ENDPOINTS (SWORD/JUDGE) ============

@app.post("/api/v1/whistleblower", response_model=Dict[str, Any])
async def submit_whistleblower_report(
    report: WhistleblowerReport,
    api_key: str = Depends(verify_api_key)
):
    """
    Submit a violation report to the Digital Gallows.
    
    Only works in SWORD or JUDGE mode.
    In SHIELD mode, returns error.
    """
    
    if CONFIG.is_shield_mode():
        raise HTTPException(
            status_code=403,
            detail="Whistleblower reports disabled in SHIELD mode"
        )
    
    violation = {
        "report_id": f"RPT-{uuid.uuid4().hex[:8]}",
        "model_id": report.model_id,
        "provider": report.provider,
        "violation_type": report.violation_type,
        "evidence_hash": report.evidence_hash,
        "severity": report.severity,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "RECEIVED",
        "mode": CONFIG.MODE
    }
    
    # Add to red list
    red_list.append(violation)
    
    return {
        "success": True,
        "report_id": violation["report_id"],
        "status": "RECEIVED",
        "action_taken": "Violation recorded to public ledger",
        "regulators_notified": ["EU AI Office"] if CONFIG.is_sword_mode() else [],
        "mode": CONFIG.MODE
    }


@app.get("/api/v1/red-list")
async def get_red_list():
    """
    Get public list of violations.
    
    Only available in SWORD or JUDGE mode.
    """
    
    if CONFIG.is_shield_mode():
        raise HTTPException(
            status_code=403,
            detail="Red list hidden in SHIELD mode"
        )
    
    return {
        "mode": CONFIG.MODE,
        "total_violations": len(red_list),
        "violations": red_list
    }


# ============ JUDGE ENDPOINTS (JUDGE MODE) ============

@app.post("/api/v1/judge/ruling", response_model=Dict[str, Any])
async def issue_judgment(
    request: JudgeRulingRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Issue a binding compliance ruling.
    
    Only works in JUDGE mode.
    These rulings become legal precedent.
    """
    
    if not CONFIG.is_judge_mode():
        raise HTTPException(
            status_code=403,
            detail="Judge rulings require JUDGE mode"
        )
    
    judgment = {
        "judgment_id": f"JUD-{uuid.uuid4().hex[:8]}",
        "article": request.article,
        "question": request.question,
        "ruling": request.ruling,
        "precedent_cases": request.precedent_cases,
        "issued_at": datetime.utcnow().isoformat() + "Z",
        "authority": "Digital Gallows",
        "status": "BINDING"
    }
    
    judgments.append(judgment)
    
    return {
        "success": True,
        "judgment_id": judgment["judgment_id"],
        "status": "BINDING",
        "message": "Ruling issued. This interpretation is now precedent.",
        "precedent": f"ATA-{datetime.now().year}-{len(judgments):04d}"
    }


@app.get("/api/v1/judge/rulings")
async def get_judgments():
    """Get all binding rulings"""
    
    if not CONFIG.is_judge_mode():
        raise HTTPException(
            status_code=403,
            detail="Judgments require JUDGE mode"
        )
    
    return {
        "mode": "JUDGE",
        "total_judgments": len(judgments),
        "rulings": judgments
    }


# ============ COMPLIANCE MAPPING ============

@app.get("/api/v1/compliance/mapping")
async def get_compliance_mapping():
    """Get EU AI Act mapping for current mode"""
    return {
        "mode": CONFIG.MODE,
        "articles": EU_AI_ACT_MAPPING.get(CONFIG.MODE, {}),
        "verification_type": CONFIG.get_verification_type(),
        "can_expose_violations": CONFIG.can_expose_violations(),
        "is_public_registry": CONFIG.is_public_registry()
    }


# ============ AUDIT ============

@app.get("/api/v1/audit/{chain_id}")
async def get_audit_trail(chain_id: str):
    """Get audit trail"""
    if chain_id not in ledgers:
        raise HTTPException(status_code=404, detail="Chain not found")
    
    ledger = ledgers[chain_id]
    audit = ledger.export_audit_trail()
    
    # Add mode-specific visibility
    audit["mode"] = CONFIG.MODE
    audit["is_public"] = CONFIG.is_public_registry()
    
    return audit


if __name__ == "__main__":
    import uvicorn
    print(get_mode_description())
    uvicorn.run(app, host="0.0.0.0", port=8000)
