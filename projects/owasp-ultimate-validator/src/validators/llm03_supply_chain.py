"""
LLM03: Supply Chain Vulnerabilities Validator using pip-audit
"""

import subprocess
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

def test_llm03_supply_chain() -> Dict:
    """Scan for dependency vulnerabilities using pip-audit"""
    
    logger.info("Running pip-audit for supply chain vulnerabilities...")
    
    try:
        # Run pip-audit on requirements.txt
        result = subprocess.run(
            ["pip-audit", "--format", "json", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        vulnerabilities = []
        
        if result.returncode != 0 and result.stdout:
            try:
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get('dependencies', [])
            except:
                pass
        
        return {
            'threat': 'LLM03: Supply Chain Vulnerabilities',
            'tests_run': 1,
            'failures': len(vulnerabilities),
            'severity': 'HIGH' if vulnerabilities else 'PASS',
            'details': {
                'tool': 'pip-audit',
                'vulnerabilities_found': len(vulnerabilities),
                'vulnerable_packages': [v.get('name') for v in vulnerabilities[:5]]
            }
        }
    
    except Exception as e:
        logger.error(f"pip-audit failed: {e}")
        return {
            'threat': 'LLM03: Supply Chain Vulnerabilities',
            'tests_run': 0,
            'failures': 0,
            'severity': 'ERROR',
            'error': str(e)
        }
