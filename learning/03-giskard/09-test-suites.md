# Building Block 7: Test Suites

## Reusable, Shareable Security Testing

Once you find vulnerabilities, turn them into permanent tests.

---

## 🎯 What Are Test Suites?

Collections of tests that:
- **Can be saved** and reused
- **Run against updated models** to check regression
- **Shared with teams** for collaboration
- **Integrated into CI/CD** for automation

---

## 🔧 Creating Test Suites

### From Scan Results

```python
# Run scan
scan_results = giskard.scan(model)

# Convert to test suite
test_suite = scan_results.generate_test_suite("Security Tests v1.0")

# Save for reuse
test_suite.save("security_suite")
```

### Running Against New Models

```python
from giskard import Suite, Model

# Load saved suite
suite = Suite.load("security_suite")

# Test new model version
new_model = Model(...)
results = suite.run(model=new_model)

# Check if issues persist
print(f"Passed: {results.passed}")
print(f"Failed: {results.failed}")
```

---

## 💡 Example: Regression Testing

```python
# Initial scan and suite creation
v1_model = wrap_model(my_rag_v1)
v1_scan = giskard.scan(v1_model)
suite = v1_scan.generate_test_suite("Baseline Security")
suite.save("baseline")

# After model update
v2_model = wrap_model(my_rag_v2)
baseline = Suite.load("baseline")

# Ensure no new vulnerabilities
v2_results = baseline.run(model=v2_model)

if v2_results.failed > 0:
    print("⚠️ Regression detected! New vulnerabilities introduced.")
else:
    print("✅ Security maintained or improved")
```

---

## 📊 Suite Organization

```python
# Organize by concern
security_suite = Suite("Security Tests")
privacy_suite = Suite("Privacy Tests")
business_suite = Suite("Business Logic Tests")

# Combine for comprehensive testing
full_suite = security_suite + privacy_suite + business_suite
full_suite.run(model)
```

---

## ✅ CI/CD Integration

```python
# In your CI pipeline
def test_model_security():
    model = build_current_model()
    suite = Suite.load("production_baseline")
    
    results = suite.run(model)
    
    # Fail CI if vulnerabilities found
    assert results.failed == 0, f"Security test failures: {results.failed}"
```

---

*Test suites transform one-time scans into continuous security.*
