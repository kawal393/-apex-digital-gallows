"""
DIGITAL GALLOWS - Sovereign Configuration
========================================

The Digital Gallows operates in THREE modes:

1. SHIELD (Lawyer) - Defend the giants, protect them from EU fines
2. SWORD (Police) - Enforce the law, expose violations  
3. JUDGE - Set the standards, decide what's compliant

The Master Position: Control all three branches.

Author: Digital Gallows Technologies
"""

import os


class SovereignConfig:
    """
    The Sovereign Configuration controls which mode the Gallows operates in.
    
    SHIELD (Lawyer): 
        - Private Merkle Tree (client-owned)
        - Internal safety flags only
        - MPC keeps weights 100% secret
        - Private compliance reports
    
    SWORD (Police):
        - Public Merkle DAG (regulator-visible)
        - Whistleblower Hook → EU AI Office
        - ZK Proofs verify the truth
        - Public Certificate of Trust
    
    JUDGE:
        - Sets the compliance standards
        - Issues binding interpretations
        - Courts cite your rulings
        - You are the law
    """
    
    def __init__(self):
        self.MODE = os.environ.get("SOVEREIGN_MODE", "SHIELD")
        self.VERSION = "2.0.0-TRIO"
        
        # Mode configurations
        self.MODES = {
            "SHIELD": {
                "description": "Lawyer Mode - Defend the Giants",
                "audit_log": "private",
                "alerting": "internal_only",
                "verification": "mpc_secret",
                "certification": "private_report",
                "exposes_violations": False,
                "public_registry": False,
            },
            "SWORD": {
                "description": "Police Mode - Enforce the Law",
                "audit_log": "public",
                "alerting": "whistleblower_eu",
                "verification": "zk_proof",
                "certification": "public_trust",
                "exposes_violations": True,
                "public_registry": True,
            },
            "JUDGE": {
                "description": "Judge Mode - Set the Standards",
                "audit_log": "canonical",
                "alerting": "court_rulings",
                "verification": "binding_interpretation",
                "certification": "legal_precedent",
                "exposes_violations": True,
                "public_registry": True,
            }
        }
    
    def get_mode_config(self):
        """Get current mode configuration"""
        return self.MODES.get(self.MODE, self.MODES["SHIELD"])
    
    def is_shield_mode(self):
        """Are we in Lawyer (defender) mode?"""
        return self.MODE == "SHIELD"
    
    def is_sword_mode(self):
        """Are we in Police (enforcer) mode?"""
        return self.MODE == "SWORD"
    
    def is_judge_mode(self):
        """Are we in Judge (authority) mode?"""
        return self.MODE == "JUDGE"
    
    def can_expose_violations(self):
        """Can we expose violations to regulators?"""
        return self.MODE in ["SWORD", "JUDGE"]
    
    def is_public_registry(self):
        """Is the registry public?"""
        return self.MODE in ["SWORD", "JUDGE"]
    
    def get_verification_type(self):
        """What type of verification?"""
        configs = {
            "SHIELD": "MPC (weights stay secret)",
            "SWORD": "ZK Proofs (verifiable truth)",
            "JUDGE": "Binding Interpretation (legal standard)"
        }
        return configs.get(self.MODE, "MPC")
    
    def __repr__(self):
        return f"<SovereignConfig mode={self.MODE} version={self.VERSION}>"


# Global configuration
CONFIG = SovereignConfig()


# EU AI Act Article References for each mode
EU_AI_ACT_MAPPING = {
    "SHIELD": {
        "article_12": "Private logging for client compliance",
        "article_13": "Transparent to client only",
        "article_14": "Internal human oversight",
        "article_15": "Client-managed accuracy",
    },
    "SWORD": {
        "article_12": "Public immutable ledger for regulators",
        "article_13": "Full transparency to EU",
        "article_14": "Sovereign Pause (kill switch)",
        "article_15": "Mandatory accuracy testing",
    },
    "JUDGE": {
        "article_12": "Canonical audit trail (legal standard)",
        "article_13": "Binding transparency rules",
        "article_14": "Court-enforced oversight",
        "article_15": "Precedent-setting accuracy standards",
    }
}


def get_mode_description():
    """Get human-readable mode description"""
    mode = CONFIG.MODE
    config = CONFIG.get_mode_config()
    return f"""
╔══════════════════════════════════════════════════════════════╗
║              DIGITAL GALLOWS - TRIO COMPLETE                  ║
╠══════════════════════════════════════════════════════════════╣
║  Current Mode: {mode:^50}║
║                                                              ║
║  {config['description']:^56}║
║                                                              ║
║  Audit Log:     {config['audit_log']:^40}║
║  Alerting:      {config['alerting']:^40}║
║  Verification:  {CONFIG.get_verification_type():^40}║
║  Certification: {config['certification']:^40}║
║                                                              ║
║  Exposes Violations: {str(CONFIG.can_expose_violations()):^37}║
║  Public Registry:    {str(CONFIG.is_public_registry()):^40}║
╚══════════════════════════════════════════════════════════════╝
"""


if __name__ == "__main__":
    print(get_mode_description())
