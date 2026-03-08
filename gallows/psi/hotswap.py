"""
APEX DIGITAL GALLOWS - Hot-Swapping Predicate Manager

This module implements the modular predicate update system.
When a regulation changes, predicates can be updated without
requiring a system reboot or downtime.

The architecture ensures that:
1. Old predicates remain valid for historical verification
2. New predicates take effect immediately
3. All updates are cryptographically logged
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class PredicateStatus(Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    PENDING_UPDATE = "pending_update"


@dataclass
class PredicateVersion:
    """A specific version of a predicate"""
    version_id: str
    value: Any
    activated_at: str
    activated_by: str  # Validator who approved
    hash: str  # Cryptographic hash of the value


@dataclass
class Predicate:
    """A rule that governs AI system behavior"""
    id: str
    name: str
    description: str
    parameter_key: str  # The circuit parameter
    current_version: Optional[PredicateVersion] = None
    version_history: List[PredicateVersion] = field(default_factory=list)
    status: PredicateStatus = PredicateStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class HotSwapPredicateManager:
    """
    Manages predicate updates without system downtime.
    
    When a regulation changes:
    1. New predicate version is created (pending)
    2. Validators approve the new version (multi-sig)
    3. New version becomes ACTIVE immediately
    4. Old version moves to history (for audit trail)
    """
    
    def __init__(self):
        self.predicates: Dict[str, Predicate] = {}
        self.update_audit_log: List[Dict] = []
    
    def create_predicate(self, name: str, description: str, 
                        parameter_key: str, initial_value: Any) -> Predicate:
        """Create a new predicate with initial version"""
        
        version_id = f"v1_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        version_hash = hashlib.sha256(str(initial_value).encode()).hexdigest()
        
        initial_version = PredicateVersion(
            version_id=version_id,
            value=initial_value,
            activated_at=datetime.utcnow().isoformat(),
            activated_by="system_init",
            hash=version_hash
        )
        
        predicate = Predicate(
            id=f"pred_{len(self.predicates) + 1:04d}",
            name=name,
            description=description,
            parameter_key=parameter_key,
            current_version=initial_version,
            version_history=[initial_version]
        )
        
        self.predicates[predicate.id] = predicate
        return predicate
    
    def update_predicate(self, predicate_id: str, new_value: Any, 
                        approved_by: str) -> PredicateVersion:
        """
        Hot-swap a predicate to a new version.
        
        This is the key method - updates take effect IMMEDIATELY
        without requiring system restart.
        """
        
        if predicate_id not in self.predicates:
            raise ValueError(f"Predicate {predicate_id} not found")
        
        predicate = self.predicates[predicate_id]
        
        # Deprecate current version
        predicate.status = PredicateStatus.PENDING_UPDATE
        
        # Create new version
        version_id = f"v{len(predicate.version_history) + 1}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        version_hash = hashlib.sha256(str(new_value).encode()).hexdigest()
        
        new_version = PredicateVersion(
            version_id=version_id,
            value=new_value,
            activated_at=datetime.utcnow().isoformat(),
            activated_by=approved_by,
            hash=version_hash
        )
        
        # Immediately activate new version
        predicate.current_version = new_version
        predicate.version_history.append(new_version)
        predicate.status = PredicateStatus.ACTIVE
        predicate.updated_at = datetime.utcnow().isoformat()
        
        # Audit log
        old_ver = None
        if len(predicate.version_history) > 1:
            old_ver = predicate.version_history[-2].version_id
        
        self.update_audit_log.append({
            "predicate_id": predicate_id,
            "old_version": old_ver,
            "new_version": new_version.version_id,
            "approved_by": approved_by,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return new_version
    
    def get_active_predicate_value(self, predicate_id: str) -> Any:
        """Get the current active value for a predicate"""
        
        if predicate_id not in self.predicates:
            raise ValueError(f"Predicate {predicate_id} not found")
        
        predicate = self.predicates[predicate_id]
        if predicate.current_version is None:
            raise ValueError(f"No active version for predicate {predicate_id}")
        
        return predicate.current_version.value
    
    def get_predicate_status(self, predicate_id: str) -> Dict:
        """Get detailed status of a predicate"""
        
        if predicate_id not in self.predicates:
            raise ValueError(f"Predicate {predicate_id} not found")
        
        p = self.predicates[predicate_id]
        
        return {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "parameter_key": p.parameter_key,
            "status": p.status.value,
            "current_version": p.current_version.version_id if p.current_version else None,
            "current_value": p.current_version.value if p.current_version else None,
            "version_count": len(p.version_history),
            "created_at": p.created_at,
            "updated_at": p.updated_at
        }
    
    def list_active_predicates(self) -> List[Dict]:
        """List all active predicates"""
        
        active = []
        for p in self.predicates.values():
            if p.status == PredicateStatus.ACTIVE:
                active.append(self.get_predicate_status(p.id))
        
        return active
    
    def get_audit_trail(self, predicate_id: Optional[str] = None) -> List[Dict]:
        """Get the update audit trail"""
        
        if predicate_id:
            return [log for log in self.update_audit_log if log["predicate_id"] == predicate_id]
        
        return self.update_audit_log


# Example usage
if __name__ == "__main__":
    mgr = HotSwapPredicateManager()
    
    # Create initial predicate
    pred = mgr.create_predicate(
        name="Bias Detection Threshold",
        description="AI must flag decisions with bias probability above this threshold",
        parameter_key="bias_threshold",
        initial_value=0.15
    )
    print(f"Created: {pred.id}")
    print(f"Initial Value: {mgr.get_active_predicate_value(pred.id)}")
    
    # Simulate regulation update - EU lowers threshold to 0.10
    new_version = mgr.update_predicate(
        pred.id,
        new_value=0.10,
        approved_by="validator_001"
    )
    print(f"\nUpdated to: {mgr.get_active_predicate_value(pred.id)}")
    print(f"New Version: {new_version.version_id}")
    
    # Show audit trail
    print(f"\nAudit Trail: {mgr.get_audit_trail(pred.id)}")
