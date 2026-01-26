---
name: Verification Audit
description: This skill should be used when verifying inputs, outputs, calculations, conclusions, and data accuracy. Use for "verify calculations", "check inputs", "validate outputs", "audit formulas", "verify logic", or when reviewing code that performs mathematical operations, financial calculations, statistical analysis, or data transformations.
version: 1.0.0
---

# Verification Audit Skill

Deep verification of inputs, outputs, calculations, conclusions, and data integrity.

## Overview

This skill provides rigorous verification of:
- Input validation completeness
- Output correctness and encoding
- Mathematical calculations and formulas
- Logical conclusions and decision trees
- Data transformations and aggregations
- Business rule implementations

## Verification Philosophy

**Trust but Verify:** Never assume calculations are correct - prove them.
**Trace End-to-End:** Follow data from input to output.
**Test Edge Cases:** Boundary conditions often reveal errors.
**Document Assumptions:** All verification assumptions must be explicit.

## Verification Dimensions

### 1. Input Verification

**Input Source Identification:**
- User input (forms, API requests)
- File uploads
- Environment variables
- Configuration files
- Database queries
- External API responses
- Message queues

**Validation Checklist:**

| Check | Description | Risk if Missing |
|-------|-------------|-----------------|
| **Type Validation** | Verify expected data type | Type confusion attacks |
| **Length Validation** | Check min/max length | Buffer overflow, DoS |
| **Range Validation** | Check numeric ranges | Integer overflow, logic errors |
| **Format Validation** | Verify format (email, date, etc.) | Injection, data corruption |
| **Whitelist Validation** | Allow only known good values | Injection attacks |
| **Encoding Validation** | Verify character encoding | Unicode attacks, mojibake |
| **Sanitization** | Remove/escape dangerous chars | XSS, injection |

**Language-Specific Patterns:**

```python
# Python - Good input validation
def process_user_input(user_id: str, amount: str) -> dict:
    # Type validation
    if not isinstance(user_id, str):
        raise TypeError("user_id must be a string")

    # Format validation
    if not re.match(r'^[a-zA-Z0-9]{8,36}$', user_id):
        raise ValueError("Invalid user_id format")

    # Type conversion with validation
    try:
        amount_decimal = Decimal(amount)
    except InvalidOperation:
        raise ValueError("amount must be a valid number")

    # Range validation
    if amount_decimal < Decimal('0.01') or amount_decimal > Decimal('1000000.00'):
        raise ValueError("amount must be between 0.01 and 1,000,000.00")

    return {"user_id": user_id, "amount": amount_decimal}
```

```javascript
// JavaScript - Good input validation
function processUserInput(userId, amount) {
    // Type validation
    if (typeof userId !== 'string') {
        throw new TypeError('userId must be a string');
    }

    // Format validation
    if (!/^[a-zA-Z0-9]{8,36}$/.test(userId)) {
        throw new Error('Invalid userId format');
    }

    // Type conversion with validation
    const amountNum = Number(amount);
    if (Number.isNaN(amountNum)) {
        throw new Error('amount must be a valid number');
    }

    // Range validation
    if (amountNum < 0.01 || amountNum > 1000000) {
        throw new RangeError('amount must be between 0.01 and 1,000,000');
    }

    return { userId, amount: amountNum };
}
```

### 2. Output Verification

**Output Correctness:**
- Verify output matches expected format
- Check all required fields present
- Validate data types in output
- Verify output encoding (UTF-8, JSON, etc.)

**Output Security:**
- XSS prevention (HTML encoding)
- JSON encoding for API responses
- SQL escaping for database writes
- Command escaping for shell output

**Output Validation Checklist:**

| Check | Description | Example |
|-------|-------------|---------|
| **Format Compliance** | Matches API contract | JSON schema validation |
| **Encoding** | Proper character encoding | HTML entities for web |
| **Completeness** | All required fields | Required fields in response |
| **Accuracy** | Data matches source | Calculated totals match |
| **Sanitization** | No sensitive data leaked | PII removed from logs |

### 3. Calculation Verification

**Mathematical Accuracy:**

```python
# Common calculation errors to check for:

# 1. Integer division truncation
# BAD
result = 5 / 2  # In Python 2: 2, Python 3: 2.5
# GOOD
from __future__ import division
result = 5 / 2  # Always 2.5

# 2. Floating-point precision
# BAD
total = 0.1 + 0.2  # 0.30000000000000004
# GOOD
from decimal import Decimal
total = Decimal('0.1') + Decimal('0.2')  # 0.3

# 3. Currency calculations
# BAD
price = 19.99 * 3  # 59.97000000000001
# GOOD
from decimal import Decimal, ROUND_HALF_UP
price = Decimal('19.99') * 3
price = price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# 4. Percentage calculations
# BAD
discount = price * 0.15  # Floating point error
# GOOD
discount = (price * Decimal('15')) / Decimal('100')

# 5. Date/time calculations
# BAD
from datetime import datetime, timedelta
end_date = start_date + timedelta(days=30)  # What about months?
# GOOD
from dateutil.relativedelta import relativedelta
end_date = start_date + relativedelta(months=1)
```

**Financial Calculations:**

| Operation | Requirement | Common Error |
|-----------|-------------|--------------|
| **Interest** | Compound vs Simple | Using wrong formula |
| **Tax** | Proper rounding | Cumulative rounding errors |
| **Currency** | 2-4 decimal places | Floating-point errors |
| **Percentages** | Basis points | Division order |
| **Amortization** | Day count conventions | 30/360 vs Actual/365 |

**Verification Steps:**
1. Identify all calculations in code
2. Document the formula being implemented
3. Create test cases with known results
4. Test boundary conditions
5. Test with actual business data
6. Verify rounding behavior

### 4. Business Logic Verification

**State Machine Verification:**
```
States: [DRAFT, PENDING, APPROVED, REJECTED, CANCELLED]

Allowed Transitions:
- DRAFT → PENDING (submit)
- PENDING → APPROVED (approve)
- PENDING → REJECTED (reject)
- PENDING → DRAFT (return)
- APPROVED → CANCELLED (cancel, within 24h)
- REJECTED → DRAFT (revise)

Verify:
✓ All transitions explicitly defined
✓ Invalid transitions blocked
✓ Guards/conditions checked
✓ Side effects triggered correctly
✓ Audit trail recorded
```

**Decision Tree Verification:**
```
For each decision point:
1. Document the condition
2. Verify both branches implemented
3. Check boundary conditions
4. Verify default/else case
5. Test all paths
```

### 5. Data Transformation Verification

**Transformation Types:**

| Type | Verification |
|------|--------------|
| **Mapping** | Source → Target field mapping correct |
| **Filtering** | Correct records included/excluded |
| **Aggregation** | Sum/count/avg calculations accurate |
| **Normalization** | Data format standardized |
| **Enrichment** | Additional data correct |
| **Deduplication** | Correct records kept |

**ETL Verification:**
```python
# Verify row counts
assert source_count == target_count + rejected_count

# Verify aggregations
assert sum(detail_amounts) == header_total

# Verify no data loss
assert set(source_ids) == set(target_ids) | set(rejected_ids)

# Verify transformations
for source, target in zip(source_data, target_data):
    assert transform(source) == target
```

### 6. Statistical Calculation Verification

**Common Statistical Errors:**

| Statistic | Common Error | Correct Implementation |
|-----------|--------------|----------------------|
| **Mean** | Integer division | Use float division |
| **Median** | Even count handling | Average middle two |
| **Std Dev** | Population vs Sample | Use n-1 for sample |
| **Percentile** | Interpolation method | Document method used |
| **Correlation** | Causation assumption | Only report correlation |

### 7. API Contract Verification

**Request Verification:**
```json
{
    "endpoint": "/api/v1/orders",
    "method": "POST",
    "request_schema": {
        "customer_id": "string, required, uuid format",
        "items": "array, required, min 1 item",
        "total": "number, required, >= 0"
    },
    "verify": [
        "All required fields present",
        "Types match schema",
        "Formats validated",
        "Business rules checked"
    ]
}
```

**Response Verification:**
```json
{
    "response_schema": {
        "order_id": "string, uuid",
        "status": "string, enum: [created, pending, confirmed]",
        "created_at": "string, ISO 8601 datetime",
        "total": "number, 2 decimal places"
    },
    "verify": [
        "Status code correct",
        "Content-Type header set",
        "Response matches schema",
        "Sensitive data not leaked"
    ]
}
```

## Verification Scripts

### Calculation Verifier

Use `${CLAUDE_PLUGIN_ROOT}/skills/verification-audit/scripts/verify-calculations.py`:

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/verification-audit/scripts/verify-calculations.py <file> --trace
```

**Options:**
- `--trace`: Show step-by-step calculation trace
- `--test-cases`: Run built-in test cases
- `--format`: Output format (text, json)

### Input Validator

Use `${CLAUDE_PLUGIN_ROOT}/skills/verification-audit/scripts/verify-inputs.py`:

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/verification-audit/scripts/verify-inputs.py <file>
```

## Verification Report Format

```markdown
## Verification Audit Report

### Input Verification
| Input | Source | Validation | Status |
|-------|--------|------------|--------|
| user_id | API param | Format, Length | ✓ |
| amount | Request body | Type, Range | ✗ Missing range |

### Calculation Verification
| Calculation | Formula | Test Result | Status |
|-------------|---------|-------------|--------|
| Total | sum(items) | 100.00 = 100.00 | ✓ |
| Tax | total * 0.08 | 8.00 = 8.0000001 | ⚠ Precision |

### Output Verification
| Output | Format | Encoding | Status |
|--------|--------|----------|--------|
| JSON response | Valid | UTF-8 | ✓ |
| HTML template | Valid | HTML entities | ✗ XSS risk |

### Business Logic Verification
| Rule | Implementation | Test | Status |
|------|----------------|------|--------|
| Min order $10 | Line 45 | Tested | ✓ |
| Max items 100 | Missing | N/A | ✗ |
```

## Common Issues by Severity

### Critical
- Missing input validation allowing injection
- Incorrect financial calculations
- Data loss in transformations
- Unvalidated outputs causing XSS

### High
- Floating-point errors in currency
- Missing boundary validation
- Incorrect date calculations
- Statistical errors affecting decisions

### Medium
- Inconsistent validation across inputs
- Missing null checks
- Rounding inconsistencies
- Incomplete output encoding

### Low
- Redundant validation
- Over-precise calculations
- Missing input trimming
- Verbose error messages
