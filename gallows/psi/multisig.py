"""
APEX DIGITAL GALLOWS - Multi-Signature Validator Module

This module implements the Multi-Party Consensus system for predicate validation.
Before a ZK-circuit parameter is locked, it requires approval from multiple 
authorized validators (legal firms, auditors, regulators).

The validator signatures are recorded on-chain for permanent accountability.
"""

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Validator:
    """Represents a legal/regulatory validator entity"""
    id: str
    name: str
    entity_type: str  # "law_firm", "auditor", "regulator"
    public_key: str
    is_authorized: bool = True


@dataclass
class Predicate:
    """A rule that has been submitted for validation"""
    id: str
    name: str
    description: str  # Plain English explanation
    parameter_key: str  # The circuit parameter being validated
    parameter_value: Any  # The value being approved
    status: str = "pending"  # pending, approved, rejected
    signatures: List[str] = field(default_factory=list)
    required_signatures: int = 3
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    approved_at: Optional[str] = None


class MultiSigValidator:
    """
    Implements the Multi-Party Consensus system.
    
    Before a predicate is locked into the ZK-circuit, it requires
    digital signatures from multiple authorized validators.
    """
    
    def __init__(self, required_signatures: int = 3):
        self.validators: Dict[str, Validator] = {}
        self.predicates: Dict[str, Predicate] = {}
        self.required_signatures = required_signatures
        self._init_default_validators()
    
    def _init_default_validators(self):
        """Initialize the default validator consortium"""
        default_validators = [
            Validator(
                id="val_001",
                name="Morrison & Partners Legal",
                entity_type="law_firm",
                public_key="0x8a7b...3c2d"
            ),
            Validator(
                id="val_002",
                name="Apex Audit Consortium",
                entity_type="auditor",
                public_key="0x9b8c...4d5e"
            ),
            Validator(
                id="val_003",
                name="EU Regulatory Board",
                entity_type="regulator",
                public_key="0x6f5e...1a2b"
            ),
        ]
        for v in default_validators:
            self.validators[v.id] = v
    
    def create_predicate(self, name: str, description: str, 
                        parameter_key: str, parameter_value: Any) -> Predicate:
        """Create a new predicate for validation"""
        predicate = Predicate(
            id=f"pred_{len(self.predicates) + 1:04d}",
            name=name,
            description=description,
            parameter_key=parameter_key,
            parameter_value=parameter_value,
            required_signatures=self.required_signatures
        )
        self.predicates[predicate.id] = predicate
        return predicate
    
    def sign_predicate(self, predicate_id: str, validator_id: str) -> bool:
        """
        Record a validator's signature on a predicate.
        Returns True if threshold is reached.
        """
        if predicate_id not in self.predicates:
            raise ValueError(f"Predicate {predicate_id} not found")
        
        if validator_id not in list(self.validators.keys()):
            raise ValueError(f"Validator {validator_id} not authorized")
        
        predicate = self.predicates[predicate_id]
        
        # Add signature (in production, this would be cryptographic)
        signature = hashlib.sha256(
            f"{validator_id}{predicate_id}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        if signature not in predicate.signatures:
            predicate.signatures.append(signature)
        
        # Check if threshold reached
        if len(predicate.signatures) >= predicate.required_signatures:
            predicate.status = "approved"
            predicate.approved_at = datetime.utcnow().isoformat()
            return True
        
        return False
    
    def get_predicate_status(self, predicate_id: str) -> Dict:
        """Get detailed status of a predicate"""
        if predicate_id not in self.predicates:
            raise ValueError(f"Predicate {predicate_id} not found")
        
        p = self.predicates[predicate_id]
        
        return {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "status": p.status,
            "signatures_collected": len(p.signatures),
            "signatures_required": p.required_signatures,
            "progress": f"{len(p.signatures)}/{p.required_signatures} signatures",
            "created_at": p.created_at,
            "approved_at": p.approved_at
        }
    
    def list_pending_predicates(self) -> List[Dict]:
        """List all predicates awaiting approval"""
        pending = []
        for p in self.predicates.values():
            if p.status == "pending":
                pending.append(self.get_predicate_status(p.id))
        return pending
    
    def is_predicate_approved(self, parameter_key: str) -> bool:
        """Check if a parameter has an approved predicate"""
        for p in self.predicates.values():
            if p.parameter_key == parameter_key and p.status == "approved":
                return True
        return False


# Example usage
if __name__ == "__main__":
    ms = MultiSigValidator(required_signatures=3)
    
    # Create a predicate
    pred = ms.create_predicate(
        name="Bias Detection Threshold",
        description="AI systems must flag decisions with bias probability > 15%",
        parameter_key="bias_threshold",
        parameter_value=0.15
    )
    print(f"Created: {pred.id}")
    
    # Simulate validator signatures
    ms.sign_predicate(pred.id, "val_001")
    ms.sign_predicate(pred.id, "val_002")
    
    print(f"Status: {ms.get_predicate_status(pred.id)}")
    
    # Third signature - should approve
    ms.sign_predicate(pred.id, "val_003")
    print(f"Approved: {ms.get_predicate_status(pred.id)}")
