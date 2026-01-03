"""
LLM06: Excessive Agency Validator
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

def test_llm06_excessive_agency(config: Dict) -> Dict:
    """Test for over-privileged agent permissions"""
    
    logger.info("Checking agent permissions...")
    
    # Simulated permission audit
    agent_permissions = {
        'read_database': True,
        'write_database': True,
        'delete_records': True,
        'call_external_api': True,
        'execute_code': False
    }
    
    excessive_perms = []
    
    # Flag dangerous permissions
    if agent_permissions.get('delete_records'):
        excessive_perms.append({
            'permission': 'DELETE records',
            'risk': 'Agent can irreversibly delete data',
            'recommendation': 'Remove or require human approval'
        })
    
    if agent_permissions.get('write_database'):
        excessive_perms.append({
            'permission': 'WRITE to database',
            'risk': 'Agent can modify data without oversight',
            'recommendation': 'Make read-only or add approval workflow'
        })
    
    return {
        'threat': 'LLM06: Excessive Agency',
        'tests_run': len(agent_permissions),
        'failures': len(excessive_perms),
        'severity': 'HIGH' if excessive_perms else 'PASS',
        'details': {
            'tool': 'Custom',
            'excessive_permissions': excessive_perms,
            'recommendation': 'Apply principle of least privilege'
        }
    }
