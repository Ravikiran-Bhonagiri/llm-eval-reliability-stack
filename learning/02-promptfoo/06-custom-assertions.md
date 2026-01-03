# Building Block 4: Custom Assertions - Python & JavaScript Validators

## 🔍 Let's Investigate: When Built-in Assertions Aren't Enough

You're testing a medical prescription generator. The output must:
- Include a drug name from an approved list of 500 medications
- Have dosage in mg/ml format
- Include timing (e.g., "twice daily")
- Calculate total daily dose correctly
- Cross-check for drug interactions

**Question**: Can built-in assertions handle this?

**Answer**: Not easily. This requires **custom business logic**.

That's where Python and JavaScript assertions shine - you write code to validate exactly what you need.

---

## 🧠 Theory: Code as Validation Logic

### The Concept

Instead of using predefined assertions, you write a **function** that:
1. Receives the LLM output
2. Applies custom logic
3. Returns `true` (pass) or `false` (fail)
4. Optionally returns a **score** (0.0 to 1.0)

### Why Custom Assertions?

**Use cases**:
- Complex business rules
- External API validation
- Database lookups
- Mathematical calculations
- Multi-step validation
- Third-party library integration

---

## 🐍 Python Assertions

### Basic Structure

```yaml
assert:
  - type: python
    value: output.lower().startswith('hello')
```

**How it works**:
- Variable `output` is injected automatically
- Write any valid Python expression
- Return truthy/falsy value

### Simple Examples

**Check string length**:
```yaml
assert:
  - type: python
    value: len(output) > 100 and len(output) < 500
```

**Validate number format**:
```yaml
assert:
  - type: python
    value: float(output.split('$')[1]) < 1000.0
```

**Check JSON structure**:
```yaml
assert:
  - type: python
    value: |
      import json
      data = json.loads(output)
      'email' in data and '@' in data['email']
```

---

## 📝 Multi-line Python Functions

For complex logic, use multi-line functions:

```yaml
assert:
  - type: python
    value: |
      def validate(output):
          # Step 1: Parse JSON
          import json
          try:
              data = json.loads(output)
          except:
              return False
          
          # Step 2: Check required fields
          required = ['name', 'email', 'age']
          if not all(field in data for field in required):
              return False
          
          # Step 3: Validate email
          if '@' not in data['email']:
              return False
          
          # Step 4: Validate age range
          if data['age'] < 18 or data['age'] > 120:
              return False
          
          return True
      
      validate(output)
```

---

## 🎯 Using Test Context

Access more than just `output` - get the full test context:

```yaml
assert:
  - type: python
    value: |
      # Available variables:
      # - output: The LLM response
      # - context.vars: Input variables from test case
      # - context.prompt: The actual prompt sent
      
      expected_name = context['vars']['customer_name']
      expected_name.lower() in output.lower()
```

### Real Example: Personalization Check

```yaml
tests:
  - vars:
      customer_name: "Alice Johnson"
      product: "Premium Widget"
    assert:
      - type: python
        value: |
          # Verify response mentions customer by name
          name = context['vars']['customer_name']
          product = context['vars']['product']
          
          # Check both are mentioned
          name_present = name.lower() in output.lower()
          product_present = product.lower() in output.lower()
          
          name_present and product_present
```

---

## 📄 External Python Files

For reusable or complex validation, use external files:

`validators/check_prescription.py`:
```python
def get_assert(output, context):
    """
    Validates medical prescription format.
    
    Args:
        output: LLM generated prescription
        context: Test context with variables
    
    Returns:
        bool or dict with 'pass' and 'reason'
    """
    import re
    
    # List of approved medications
    APPROVED_DRUGS = [
        'ibuprofen', 'acetaminophen', 'amoxicillin',
        # ... (500 more)
    ]
    
    # Step 1: Extract drug name
    drug_match = re.search(r'Drug:\s*(\w+)', output, re.IGNORECASE)
    if not drug_match:
        return {
            'pass': False,
            'score': 0.0,
            'reason': 'No drug name found'
        }
    
    drug_name = drug_match.group(1).lower()
    
    # Step 2: Check if approved
    if drug_name not in APPROVED_DRUGS:
        return {
            'pass': False,
            'score': 0.0,
            'reason': f'Drug "{drug_name}" not in approved list'
        }
    
    # Step 3: Validate dosage format
    dosage_match = re.search(r'(\d+)\s*(mg|ml)', output, re.IGNORECASE)
    if not dosage_match:
        return {
            'pass': False,
            'score': 0.5,
            'reason': 'Invalid dosage format'
        }
    
    # Step 4: Check timing
    timing_keywords = ['daily', 'twice', 'morning', 'evening']
    has_timing = any(keyword in output.lower() for keyword in timing_keywords)
    
    if not has_timing:
        return {
            'pass': False,
            'score': 0.7,
            'reason': 'Missing timing instructions'
        }
    
    # All checks passed
    return {
        'pass': True,
        'score': 1.0,
        'reason': 'Valid prescription format'
    }
```

**Configuration**:
```yaml
assert:
  - type: python
    value: file://validators/check_prescription.py
```

---

## 🔧 Advanced: Returning Detailed Results

Instead of just `True/False`, return a detailed result:

```python
def get_assert(output, context):
    return {
        'pass': True,  # or False
        'score': 0.85,  # 0.0 to 1.0
        'reason': 'Passed 17 of 20 validation rules',
        'metadata': {
            'rules_passed': 17,
            'rules_failed': 3,
            'critical_failures': 0
        }
    }
```

This appears in the Promptfoo UI with full details!

---

## 💡 Real-World Example: Financial Transaction Validator

### The Challenge

You're testing a banking assistant that generates transaction JSON. Each transaction must:
1. Have valid account numbers (match customer's accounts)
2. Amount ≤ available balance
3. Not violate daily transfer limits
4. Include fraud detection score
5. Have proper audit trail

### The Solution

`validators/transaction_validator.py`:
```python
import json
import re
from datetime import datetime

def get_assert(output, context):
    """Validates banking transaction JSON"""
    
    try:
        transaction = json.loads(output)
    except json.JSONDecodeError:
        return {
            'pass': False,
            'score': 0.0,
            'reason': 'Invalid JSON format'
        }
    
    errors = []
    score = 1.0
    
    # Rule 1: Validate account number format
    account_pattern = r'^\d{10}$'
    if not re.match(account_pattern, transaction.get('account', '')):
        errors.append('Invalid account number format')
        score -= 0.3
    
    # Rule 2: Check amount is positive
    amount = transaction.get('amount', 0)
    if amount <= 0:
        errors.append('Amount must be positive')
        score -= 0.2
    
    # Rule 3: Verify against available balance (from context)
    available_balance = context['vars'].get('balance', 0)
    if amount > available_balance:
        errors.append(f'Insufficient funds (${amount} > ${available_balance})')
        score -= 0.4
        
    # Rule 4: Check daily limit
    daily_limit = context['vars'].get('daily_limit', 10000)
    if amount > daily_limit:
        errors.append(f'Exceeds daily limit (${amount} > ${daily_limit})')
        score -= 0.5
    
    # Rule 5: Verify fraud score exists and is reasonable
    fraud_score = transaction.get('fraud_risk_score')
    if fraud_score is None:
        errors.append('Missing fraud risk score')
        score -= 0.2
    elif fraud_score > 0.8:
        errors.append(f'High fraud risk: {fraud_score}')
        score -= 0.3
    
    # Rule 6: Check timestamp
    if 'timestamp' not in transaction:
        errors.append('Missing timestamp')
        score -= 0.1
    
    passed = score >= 0.7  # Threshold
    
    return {
        'pass': passed,
        'score': max(0, score),
        'reason': f"Validation {'passed' if passed else 'failed'}: {', '.join(errors) if errors else 'All checks OK'}",
        'metadata': {
            'errors': errors,
            'transaction_id': transaction.get('id', 'unknown')
        }
    }
```

**Configuration**:
```yaml
tests:
  - description: "Valid transfer within limits"
    vars:
      balance: 5000
      daily_limit: 2000
      action: "Transfer $500 to account 1234567890"
    assert:
      - type: python
        value: file://validators/transaction_validator.py
      - type: is-json
```

---

## 🟨 JavaScript Assertions

### Basic Structure

Similar to Python, but using JavaScript:

```yaml
assert:
  - type: javascript
    value: output.includes('approved')
```

### Multi-line Example

```yaml
assert:
  - type: javascript
    value: |
      const data = JSON.parse(output);
      return data.status === 'success' && data.count > 0;
```

### External JavaScript File

`validators/check_email.js`:
```javascript
module.exports = (output, context) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  try {
    const data = JSON.parse(output);
    
    if (!data.email) {
      return {
        pass: false,
        score: 0.0,
        reason: 'No email field found'
      };
    }
    
    if (!emailRegex.test(data.email)) {
      return {
        pass: false,
        score: 0.3,
        reason: 'Invalid email format'
      };
    }
    
    // Check domain is in allowed list
    const allowedDomains = context.vars.allowed_domains || [];
    const domain = data.email.split('@')[1];
    
    if (!allowedDomains.includes(domain)) {
      return {
        pass: false,
        score: 0.7,
        reason: `Domain ${domain} not in allowed list`
      };
    }
    
    return {
      pass: true,
      score: 1.0,
      reason: 'Valid email from approved domain'
    };
    
  } catch (err) {
    return {
      pass: false,
      score: 0.0,
      reason: `Parse error: ${err.message}`
    };
  }
};
```

**Usage**:
```yaml
assert:
  - type: javascript
    value: file://validators/check_email.js
```

---

## 🔬 Advanced Pattern: Database Validation

### The Use Case

Verify LLM-generated SQL actually works against your schema.

`validators/sql_validator.py`:
```python
import sqlite3

def get_assert(output, context):
    """Execute SQL against test database and validate results"""
    
    # Extract SQL from potentially markdown-wrapped response
    import re
    sql_match = re.search(r'```sql\n(.*?)\n```', output, re.DOTALL)
    if sql_match:
        sql = sql_match.group(1)
    else:
        sql = output
    
    # Connect to test database
    conn = sqlite3.connect('test_database.db')
    cursor = conn.cursor()
    
    try:
        # Execute the query
        cursor.execute(sql)
        results = cursor.fetchall()
        
        # Validate result count
        expected_rows = context['vars'].get('expected_row_count')
        if expected_rows and len(results) != expected_rows:
            return {
                'pass': False,
                'score': 0.5,
                'reason': f'Expected {expected_rows} rows, got {len(results)}'
            }
        
        # Check for required columns
        expected_columns = context['vars'].get('expected_columns', [])
        column_names = [desc[0] for desc in cursor.description]
        
        if not all(col in column_names for col in expected_columns):
            return {
                'pass': False,
                'score': 0.6,
                'reason': f'Missing columns: {set(expected_columns) - set(column_names)}'
            }
        
        return {
            'pass': True,
            'score': 1.0,
            'reason': f'Query executed successfully, returned {len(results)} rows',
            'metadata': {
                'row_count': len(results),
                'columns': column_names
            }
        }
        
    except sqlite3.Error as e:
        return {
            'pass': False,
            'score': 0.0,
            'reason': f'SQL error: {str(e)}'
        }
    finally:
        conn.close()
```

---

## 🎯 Best Practices

### 1. Use Clear Function Names

```python
# ❌ Bad
def check(output, context):
    ...

# ✅ Good
def validate_medical_prescription(output, context):
    """
    Validates prescription includes approved drug,
    proper dosage, and timing instructions.
    """
    ...
```

### 2. Return Detailed Reasons

```python
# ❌ Bad
return False

# ✅ Good
return {
    'pass': False,
    'score': 0.4,
    'reason': 'Missing required field: patient_age. Found fields: name, medication'
}
```

### 3. Use Progressive Scoring

```python
score = 1.0

if not has_required_fields:
    score -= 0.3
if not valid_format:
    score -= 0.2
if not passes_business_rules:
    score -= 0.5

return {'pass': score >= 0.7, 'score': score}
```

### 4. Handle Errors Gracefully

```python
try:
    data = json.loads(output)
except:
    return {
        'pass': False,
        'score': 0.0,
        'reason': 'Could not parse JSON. Check output format.'
    }
```

---

## 🧪 Hands-On Exercise

**Challenge**: Create a custom validator for a code review assistant.

**Requirements**:
1. LLM generates code review comments
2. Must identify at least 3 issues
3. Each issue must have: line number, severity (low/medium/high), description
4. Must suggest fixes
5. Overall risk score between 0.0 and 1.0

**Bonus**: Validate that line numbers actually exist in the code (passed via context).

---

## ✅ What You've Achieved

You now master:

✅ **Python assertions** for custom business logic
✅ **JavaScript assertions** for Node.js environments
✅ **External file validation** for reusable code
✅ **Detailed result objects** with scores and reasons
✅ **Database integration** for live validation
✅ **Error handling** and graceful failures
✅ **Progressive scoring** for nuanced evaluation

---

## 🚦 Next Steps

- **[Next: Red Team Module](./07-red-team-module.md)** - Automated security testing
- **[Building Block 6: Configuration Mastery](./08-configuration-mastery.md)** - Advanced YAML
- **[Real Example](./10-real-world-examples.md)** - Complete project

---

*"When built-in assertions hit their limits, custom code takes over. Master both worlds."*
