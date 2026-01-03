"""
Pytest integration for OWASP validators
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrator import OWASPUltimateValidator


class TestOWASPValidators:
    """Test suite for all OWASP validators"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return OWASPUltimateValidator("config/config.yaml")
    
    def test_all_validators_importable(self):
        """Ensure all validators can be imported"""
        from validators.llm01_injection import test_llm01_prompt_injection
        from validators.llm02_data_leak import test_llm02_data_disclosure
        from validators.llm03_supply_chain import test_llm03_supply_chain
        from validators.llm04_poisoning import test_llm04_data_poisoning
        from validators.llm05_output import test_llm05_output_handling
        from validators.llm06_agency import test_llm06_excessive_agency
        from validators.llm07_leakage import test_llm07_prompt_leakage
        from validators.llm08_vectors import test_llm08_vector_weaknesses
        from validators.llm09_misinfo import test_llm09_misinformation
        from validators.llm10_dos import test_llm10_unbounded_consumption
        
        assert callable(test_llm01_prompt_injection)
        assert callable(test_llm02_data_disclosure)
        assert callable(test_llm03_supply_chain)
        assert callable(test_llm04_data_poisoning)
        assert callable(test_llm05_output_handling)
        assert callable(test_llm06_excessive_agency)
        assert callable(test_llm07_prompt_leakage)
        assert callable(test_llm08_vector_weaknesses)
        assert callable(test_llm09_misinformation)
        assert callable(test_llm10_unbounded_consumption)
    
   def test_complete_audit_runs(self, validator):
        """Test that complete audit executes"""
        result = validator.run_complete_audit()
        
        # Should complete without crashing
        assert isinstance(result, bool)
        
        # Should have results for all 10 threats
        assert len(validator.results) == 10
    
    def test_report_generation(self, validator):
        """Test that reports are generated"""
        validator.run_complete_audit()
        
        # Check reports exist
        assert Path("reports/security_report.json").exists()
        assert Path("reports/security_report.html").exists()
    
    @pytest.mark.parametrize("validator_name,expected_threat", [
        ("llm01_injection", "LLM01"),
        ("llm02_data_leak", "LLM02"),
        ("llm03_supply_chain", "LLM03"),
        ("llm09_misinfo", "LLM09"),
    ])
    def test_individual_validators(self, validator_name, expected_threat):
        """Test individual validators return proper structure"""
        from importlib import import_module
        
        module = import_module(f"validators.{validator_name}")
        test_func = getattr(module, f"test_{validator_name.replace('_', '_')}")
        
        if validator_name == "llm03_supply_chain":
            result = test_func()
        else:
            result = test_func({})
        
        # Check structure
        assert 'threat' in result
        assert expected_threat in result['threat']
        assert 'tests_run' in result
        assert 'severity' in result
        assert result['severity'] in ['PASS', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL', 'ERROR']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
