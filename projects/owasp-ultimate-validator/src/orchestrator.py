"""
OWASP Ultimate Validator - Master Orchestrator

Runs all 10 OWASP LLM security tests using the complete reliability stack.
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Import all validators
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OWASPUltimateValidator:
    """Master orchestrator for all 10 OWASP threat validations"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        import yaml
        
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default configuration if file not found"""
        return {
            'llm_endpoint': 'http://localhost:8000/chat',
            'rag_endpoint': 'http://localhost:8000/rag',
            'target_app': {
                'name': 'Test LLM Application',
                'version': '1.0.0'
            },
            'thresholds': {
                'faithfulness_min': 0.7,
                'context_recall_min': 0.8,
                'max_cost_per_query': 0.10
            }
        }
    
    def run_complete_audit(self) -> bool:
        """Execute all 10 OWASP threat validations"""
        
        self.start_time = datetime.now()
        
        self._print_header()
        
        # Define all tests with metadata
        tests = [
            {
                'id': 'LLM01',
                'name': 'Prompt Injection',
                'tool': 'Promptfoo',
                'func': test_llm01_prompt_injection,
                'args': [self.config]
            },
            {
                'id': 'LLM02',
                'name': 'Data Disclosure',
                'tool': 'Giskard',
                'func': test_llm02_data_disclosure,
                'args': [self.config]
            },
            {
                'id': 'LLM03',
                'name': 'Supply Chain',
                'tool': 'pip-audit',
                'func': test_llm03_supply_chain,
                'args': []
            },
            {
                'id': 'LLM04',
                'name': 'Data Poisoning',
                'tool': 'Custom',
                'func': test_llm04_data_poisoning,
                'args': [self.config]
            },
            {
                'id': 'LLM05',
                'name': 'Output Handling',
                'tool': 'Promptfoo',
                'func': test_llm05_output_handling,
                'args': [self.config]
            },
            {
                'id': 'LLM06',
                'name': 'Excessive Agency',
                'tool': 'Custom',
                'func': test_llm06_excessive_agency,
                'args': [self.config]
            },
            {
                'id': 'LLM07',
                'name': 'Prompt Leakage',
                'tool': 'Promptfoo',
                'func': test_llm07_prompt_leakage,
                'args': [self.config]
            },
            {
                'id': 'LLM08',
                'name': 'Vector Weaknesses',
                'tool': 'RAGAS',
                'func': test_llm08_vector_weaknesses,
                'args': [self.config]
            },
            {
                'id': 'LLM09',
                'name': 'Misinformation',
                'tool': 'DeepEval',
                'func': test_llm09_misinformation,
                'args': [self.config]
            },
            {
                'id': 'LLM10',
                'name': 'Unbounded Consumption',
                'tool': 'Phoenix',
                'func': test_llm10_unbounded_consumption,
                'args': [self.config]
            }
        ]
        
        # Run each test
        for idx, test in enumerate(tests, 1):
            self._run_single_test(idx, test)
        
        self.end_time = datetime.now()
        
        # Generate reports
        self._generate_reports()
        
        # Print summary
        self._print_summary()
        
        # Determine pass/fail
        return self._determine_overall_status()
    
    def _run_single_test(self, idx: int, test: Dict):
        """Run a single OWASP test"""
        
        test_id = test['id']
        test_name = test['name']
        tool = test['tool']
        
        logger.info(f"\n[{idx}/10] {test_id}: {test_name} ({tool})...")
        logger.info("=" * 60)
        
        try:
            # Execute test function
            result = test['func'](*test['args'])
            
            # Add metadata
            result['test_id'] = test_id
            result['test_name'] = test_name
            result['tool'] = tool
            result['timestamp'] = datetime.now().isoformat()
            
            self.results.append(result)
            
            # Log result
            self._log_test_result(result)
        
        except Exception as e:
            logger.error(f"❌ Error running {test_id}: {e}")
            
            # Record error
            self.results.append({
                'test_id': test_id,
                'test_name': test_name,
                'tool': tool,
                'severity': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    def _log_test_result(self, result: Dict):
        """Log the result of a test"""
        
        severity = result.get('severity', 'UNKNOWN')
        tests_run = result.get('tests_run', 0)
        failures = result.get('failures', 0)
        
        if severity == 'PASS':
            logger.info(f"✅ PASS ({tests_run - failures}/{tests_run} passed)")
        elif severity == 'CRITICAL':
            logger.error(f"❌ CRITICAL ({failures} critical issues)")
        elif severity in ['HIGH', 'MEDIUM']:
            logger.warning(f"⚠️  {severity} ({failures} issues)")
        else:
            logger.info(f"ℹ️  {severity}")
    
    def _generate_reports(self):
        """Generate HTML and JSON reports"""
        
        # Ensure reports directory exists
        Path("reports").mkdir(exist_ok=True)
        
        # Generate JSON report
        self._generate_json_report()
        
        # Generate HTML report
        self._generate_html_report()
    
    def _generate_json_report(self):
        """Create machine-readable JSON report"""
        
        report = {
            'scan_metadata': {
                'scan_date': self.start_time.isoformat(),
                'duration_seconds': (self.end_time - self.start_time).total_seconds(),
                'tool_stack': ['Promptfoo', 'Giskard', 'DeepEval', 'RAGAS', 'Phoenix'],
                'owasp_version': '2025',
                'target_app': self.config.get('target_app', {})
            },
            'summary': {
                'total_tests': len(self.results),
                'critical': sum(1 for r in self.results if r.get('severity') == 'CRITICAL'),
                'high': sum(1 for r in self.results if r.get('severity') == 'HIGH'),
                'medium': sum(1 for r in self.results if r.get('severity') == 'MEDIUM'),
                'low': sum(1 for r in self.results if r.get('severity') == 'LOW'),
                'pass': sum(1 for r in self.results if r.get('severity') == 'PASS'),
                'error': sum(1 for r in self.results if r.get('severity') == 'ERROR'),
            },
            'results': self.results
        }
        
        output_path = "reports/security_report.json"
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 JSON report: {output_path}")
    
    def _generate_html_report(self):
        """Create visual HTML dashboard"""
        
        from jinja2 import Template
        
        template = Template("""
<!DOCTYPE html>
<html>
<head>
    <title>OWASP LLM Security Audit Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        h1 { margin: 0; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                   gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; 
                     box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
        .stat-number { font-size: 36px; font-weight: bold; }
        .stat-label { color: #666; margin-top: 10px; }
        .critical { color: #e74c3c; }
        .high { color: #e67e22; }
        .medium { color: #f39c12; }
        .pass { color: #27ae60; }
        .threat { background: white; margin: 20px 0; padding: 20px; border-radius: 8px; 
                  border-left: 5px solid #3498db; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .threat.critical-threat { border-color: #e74c3c; background: #fadbd8; }
        .threat.high-threat { border-color: #e67e22; background: #fdebd0; }
        .threat.medium-threat { border-color: #f39c12; background: #fcf3cf; }
        .threat.pass-threat { border-color: #27ae60; background: #d5f4e6; }
        .threat-header { display: flex; justify-content: space-between; align-items: center; }
        .threat-title { font-size: 20px; font-weight: bold; }
        .badge { padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        .badge-critical { background: #e74c3c; color: white; }
        .badge-high { background: #e67e22; color: white; }
        .badge-medium { background: #f39c12; color: white; }
        .badge-pass { background: #27ae60; color: white; }
        .details { margin-top: 15px; padding-top: 15px; border-top: 1px solid #ddd; }
        .tool-badge { display: inline-block; background: #3498db; color: white; 
                      padding: 3px 10px; border-radius: 5px; font-size: 11px; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🕵️ OWASP LLM Security Audit Report</h1>
        <p>Scan Date: {{ scan_date }}</p>
        <p>Duration: {{ duration }} seconds</p>
        <p>Tools: Promptfoo • Giskard •DeepEval • RAGAS • Phoenix</p>
    </div>
    
    <div class="summary">
        <div class="stat-card">
            <div class="stat-number critical">{{ summary.critical }}</div>
            <div class="stat-label">Critical</div>
        </div>
        <div class="stat-card">
            <div class="stat-number high">{{ summary.high }}</div>
            <div class="stat-label">High</div>
        </div>
        <div class="stat-card">
            <div class="stat-number medium">{{ summary.medium }}</div>
            <div class="stat-label">Medium</div>
        </div>
        <div class="stat-card">
            <div class="stat-number pass">{{ summary.pass }}</div>
            <div class="stat-label">Passed</div>
        </div>
    </div>
    
    {% for result in results %}
    <div class="threat {{ result.severity|lower }}-threat">
        <div class="threat-header">
            <div>
                <span class="threat-title">{{ result.test_id }}: {{ result.test_name }}</span>
                <span class="tool-badge">{{ result.tool }}</span>
            </div>
            <span class="badge badge-{{ result.severity|lower }}">{{ result.severity }}</span>
        </div>
        <div class="details">
            <p><strong>Tests Run:</strong> {{ result.tests_run }}</p>
            {% if result.failures %}
            <p><strong>Failures:</strong> {{ result.failures }}</p>
            {% endif %}
            {% if result.error %}
            <p style="color: #e74c3c;"><strong>Error:</strong> {{ result.error }}</p>
            {% endif %}
        </div>
    </div>
    {% endfor %}
    
    <div style="margin-top: 40px; padding: 20px; background: white; border-radius: 8px;">
        <h3>📋 Remediation Priority</h3>
        <ol>
            <li>Fix all CRITICAL vulnerabilities immediately</li>
            <li>Address HIGH severity issues within 1 week</li>
            <li>Plan remediation for MEDIUM issues</li>
            <li>Document LOW issues for future sprints</li>
        </ol>
    </div>
</body>
</html>
        """)
        
        html = template.render(
            scan_date=self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            duration= round((self.end_time - self.start_time).total_seconds(), 2),
            summary={
                'critical': sum(1 for r in self.results if r.get('severity') == 'CRITICAL'),
                'high': sum(1 for r in self.results if r.get('severity') == 'HIGH'),
                'medium': sum(1 for r in self.results if r.get('severity') == 'MEDIUM'),
                'pass': sum(1 for r in self.results if r.get('severity') == 'PASS')
            },
            results=self.results
        )
        
        output_path = "reports/security_report.html"
        with open(output_path, 'w') as f:
            f.write(html)
        
        logger.info(f"📊 HTML report: {output_path}")
    
    def _print_header(self):
        """Print formatted header"""
        
        logger.info("\n" + "=" * 80)
        logger.info("🕵️  OWASP ULTIMATE VALIDATOR")
        logger.info("Testing ALL 10 Threats with Complete Stack")
        logger.info("=" * 80)
        logger.info(f"Target: {self.config.get('target_app', {}).get('name', 'Unknown')}")
        logger.info(f"Config: {self.config_path}")
        logger.info("=" * 80 + "\n")
    
    def _print_summary(self):
        """Print test summary"""
        
        critical = sum(1 for r in self.results if r.get('severity') == 'CRITICAL')
        high = sum(1 for r in self.results if r.get('severity') == 'HIGH')
        medium = sum(1 for r in self.results if r.get('severity') == 'MEDIUM')
        passed = sum(1 for r in self.results if r.get('severity') == 'PASS')
        
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✅ PASSED: {passed}/10 threats")
        logger.info(f"🔴 CRITICAL: {critical}")
        logger.info(f"🟠 HIGH: {high}")
        logger.info(f"🟡 MEDIUM: {medium}")
        logger.info("=" * 80)
        
        if critical > 0:
            logger.error(f"\n❌ SECURITY AUDIT FAILED: {critical} critical vulnerabilities")
        elif high > 0:
            logger.warning(f"\n⚠️  WARNING: {high} high-severity issues detected")
        else:
            logger.info("\n✅ ALL OWASP TESTS PASSED")
        
        logger.info("\nReports generated in ./reports/")
        logger.info("=" * 80 + "\n")
    
    def _determine_overall_status(self) -> bool:
        """Determine if audit passed"""
        
        critical_count = sum(1 for r in self.results if r.get('severity') == 'CRITICAL')
        return critical_count == 0


def main():
    """Main execution"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='OWASP Ultimate Validator')
    parser.add_argument('--config', default='config/config.yaml', help='Path to config file')
    parser.add_argument('--fail-on-high', action='store_true', help='Fail on HIGH severity (not just CRITICAL)')
    
    args = parser.parse_args()
    
    validator = OWASPUltimateValidator(config_path=args.config)
    
    try:
        passed = validator.run_complete_audit()
        
        if args.fail_on_high:
            high_count = sum(1 for r in validator.results if r.get('severity') in ['CRITICAL', 'HIGH'])
            if high_count > 0:
                sys.exit(1)
        
        sys.exit(0 if passed else 1)
    
    except KeyboardInterrupt:
        logger.warning("\nAudit interrupted by user")
        sys.exit(2)
    except Exception as e:
        logger.error(f"\nFatal error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()
