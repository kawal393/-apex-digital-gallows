# APEX DIGITAL GALLOWS

**EU AI Act 2026 Compliance Platform (The Sovereign Wrapper)**

---

## What We Do

APEX DIGITAL GALLOWS provides a real-world, functional compliance platform for AI systems under the EU AI Act 2026. 

We solve the compliance headache by providing automated tools to classify risk, log AI decisions immutably, and generate required technical documentation.

---

## The EU AI Act Compliance Engine

We provide functional software to satisfy mandatory EU requirements:

| Module | Requirement | Our Solution |
|---------|-------------|--------------|
| `gallows.risk` | Risk Assessment | Automated classification against Annex III categories |
| `gallows.audit` | Article 12 (Record-Keeping) | Cryptographic SQLite Ledger (Immutable Hash Chains) |
| `gallows.policy`| Article 11 (Documentation) | Automated Technical Documentation generation |
| `Sovereign Pause`| Article 14 (Human Oversight) | API integration for human override ("Kill Switch") |

---

## Why We Built This

The EU AI Act is becoming law. In August 2026, major enforcement begins. Non-compliance penalties reach €35 million or 7% of global turnover.

Most compliance platforms are "vaporware" promising advanced Zero-Knowledge proofs that don't exist. **Digital Gallows is practical, immediate compliance software.** We don't fake cryptography; we build real audit logs and risk engines.

---

## Getting Started

### 1. The Immutable Ledger (Article 12)
Log every AI decision into a tamper-proof cryptographic database:
```python
from gallows.audit.ledger import ImmutableLedger

ledger = ImmutableLedger()
tx_hash = ledger.log_event("AI_DECISION", "gpt-4-system", {"confidence": 0.95})
print(f"Decision logged immutably: {tx_hash}")
```

### 2. Risk Classification (Annex III)
Determine if your system is High-Risk:
```python
from gallows.risk.classifier import RiskClassifier

classifier = RiskClassifier()
result = classifier.evaluate_system({
    "domain": "employment_workers_management",
    "practices": ["automated_resume_screening"]
})
print(result['risk_level']) # Output: HIGH
```

### 3. Documentation Generator (Article 11)
Generate your compliance paperwork:
```python
from gallows.policy.generator import PolicyGenerator

generator = PolicyGenerator()
doc = generator.generate_article_11_doc("HR-Screen-AI", "HIGH", "Acme Corp", "1.0")
```

---

## About

Built by **APEX INTELLIGENCE EMPIRE**
A division of ROCKYFILMS888 PTY LTD (ABN: 71 672 237 795)
Victoria, Australia

**© 2026 APEX DIGITAL GALLOWS**