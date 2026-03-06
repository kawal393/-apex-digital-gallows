"""
DIGITAL GALLOWS - Risk Assessment Engine
EU AI Act Compliance (Title III - High-Risk AI Systems)

Classifies AI systems according to the EU AI Act risk tiers:
- Unacceptable Risk (Prohibited)
- High Risk (Strict obligations)
- Limited Risk (Transparency obligations)
- Minimal/No Risk
"""

from typing import Dict, Any, List

class RiskClassifier:
    
    # EU AI Act Annex III High-Risk Categories
    HIGH_RISK_DOMAINS = [
        "biometric_identification",
        "critical_infrastructure",
        "education_vocational_training",
        "employment_workers_management",
        "essential_private_public_services",
        "law_enforcement",
        "migration_asylum_border_control",
        "administration_of_justice"
    ]
    
    # Prohibited practices (Article 5)
    UNACCEPTABLE_PRACTICES = [
        "subliminal_manipulation",
        "exploitation_of_vulnerabilities",
        "social_scoring",
        "real_time_remote_biometric_public"
    ]

    def __init__(self):
        pass

    def evaluate_system(self, system_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an AI system against EU AI Act criteria.
        
        Expected keys in system_profile:
        - domain: str
        - practices: List[str]
        - interacts_with_humans: bool
        - generates_deepfakes: bool
        """
        
        # 1. Check for Unacceptable Risk (Prohibited)
        practices = system_profile.get("practices", [])
        for practice in practices:
            if practice in self.UNACCEPTABLE_PRACTICES:
                return {
                    "risk_level": "UNACCEPTABLE",
                    "action_required": "PROHIBITED - Cease operation immediately.",
                    "articles_triggered": ["Article 5"],
                    "reasoning": f"System employs prohibited practice: {practice}"
                }

        # 2. Check for High Risk
        domain = system_profile.get("domain", "")
        if domain in self.HIGH_RISK_DOMAINS:
            return {
                "risk_level": "HIGH",
                "action_required": "Strict Compliance (Articles 8-24). Requires Conformity Assessment, Risk Management System, and CE marking.",
                "articles_triggered": ["Title III", "Annex III"],
                "reasoning": f"System operates in high-risk domain: {domain}"
            }

        # 3. Check for Limited Risk (Transparency)
        if system_profile.get("interacts_with_humans", False) or system_profile.get("generates_deepfakes", False):
            return {
                "risk_level": "LIMITED",
                "action_required": "Transparency Obligations. Must inform users they are interacting with AI.",
                "articles_triggered": ["Article 52"],
                "reasoning": "System interacts with humans or generates synthetic content."
            }

        # 4. Minimal Risk
        return {
            "risk_level": "MINIMAL",
            "action_required": "No mandatory obligations. Voluntary codes of conduct encouraged.",
            "articles_triggered": ["Title IX"],
            "reasoning": "System does not fall into higher risk categories."
        }

if __name__ == "__main__":
    classifier = RiskClassifier()
    
    # Test High Risk CV screening AI
    profile = {
        "domain": "employment_workers_management",
        "practices": ["automated_resume_screening"],
        "interacts_with_humans": False,
        "generates_deepfakes": False
    }
    
    result = classifier.evaluate_system(profile)
    print("Risk Classification Result:")
    for k, v in result.items():
        print(f"{k}: {v}")
