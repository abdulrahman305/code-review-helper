# HIPAA Technical Safeguards

## Overview

HIPAA Security Rule (45 CFR Part 164) requires covered entities and business associates to implement technical safeguards to protect electronic Protected Health Information (ePHI).

## Access Control (§164.312(a))

### Unique User Identification (Required)
**Implementation:**
- Each user has unique identifier
- No shared accounts
- User IDs cannot be reused

```python
# Example: Unique user identification
class User:
    id: UUID  # Globally unique, never reused
    employee_id: str  # Organization-specific
    username: str  # Unique within system

    @classmethod
    def create(cls, employee_id, username):
        if cls.query.filter_by(username=username).first():
            raise ValueError("Username already exists")
        return cls(id=uuid4(), employee_id=employee_id, username=username)
```

### Emergency Access Procedure (Required)
**Implementation:**
- Break-glass procedure for emergencies
- All emergency access logged
- Post-emergency review process

```python
# Example: Emergency access
def emergency_access(user, patient_id, reason):
    """Break-glass access for emergencies."""
    if not user.is_authorized_for_emergency:
        raise UnauthorizedError()

    # Log before granting access
    audit_log.record(
        event="EMERGENCY_ACCESS_INITIATED",
        user_id=user.id,
        patient_id=patient_id,
        reason=reason,
        timestamp=datetime.utcnow()
    )

    # Notify supervisors
    notify_security_team(user, patient_id, reason)

    # Grant temporary elevated access
    return grant_temporary_access(user, patient_id, duration=timedelta(hours=4))
```

### Automatic Logoff (Addressable)
**Implementation:**
- Session timeout after inactivity
- Recommended: 15-30 minutes for ePHI systems
- Longer timeouts acceptable with justification

```python
# Example: Session timeout
SESSION_TIMEOUT_MINUTES = 15

@app.before_request
def check_session_timeout():
    if current_user.is_authenticated:
        last_activity = session.get('last_activity')
        if last_activity:
            elapsed = datetime.utcnow() - last_activity
            if elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                audit_log.record("SESSION_TIMEOUT", current_user.id)
                logout_user()
                flash("Session expired due to inactivity")
                return redirect(url_for('login'))
        session['last_activity'] = datetime.utcnow()
```

### Encryption and Decryption (Addressable)
**Implementation:**
- Encrypt ePHI at rest when technically feasible
- Use AES-256 for encryption
- Implement key management

## Audit Controls (§164.312(b))

### Required Audit Events
- User authentication (success/failure)
- Access to ePHI (view, create, modify, delete)
- Permission changes
- System configuration changes
- Data export/transmission

### Audit Record Contents
```python
audit_record = {
    "timestamp": "2024-01-15T14:30:00Z",
    "event_type": "PHI_ACCESS",
    "user_id": "user123",
    "user_role": "physician",
    "patient_id": "patient456",
    "resource": "medical_record",
    "action": "VIEW",
    "reason": "treatment",
    "workstation": "WS-CLINIC-01",
    "ip_address": "10.0.1.50",
    "outcome": "SUCCESS"
}
```

### Minimum Necessary Standard
Log the specific data elements accessed:

```python
def access_patient_record(user, patient_id, fields_requested):
    """Access ePHI with minimum necessary logging."""
    # Determine allowed fields based on role
    allowed_fields = get_allowed_fields(user.role, fields_requested)

    # Fetch only allowed fields
    record = Patient.query.get(patient_id)
    data = {f: getattr(record, f) for f in allowed_fields}

    # Log with specific fields accessed
    audit_log.record(
        event="PHI_ACCESS",
        user_id=user.id,
        patient_id=patient_id,
        fields_accessed=allowed_fields,
        fields_denied=set(fields_requested) - set(allowed_fields)
    )

    return data
```

## Integrity (§164.312(c))

### Mechanism to Authenticate ePHI (Addressable)
**Implementation:**
- Checksums/hashes for data integrity
- Digital signatures for non-repudiation
- Detect unauthorized alterations

```python
import hashlib
import hmac

class PHIRecord:
    def __init__(self, data, integrity_key):
        self.data = data
        self.integrity_hash = self._compute_hash(integrity_key)

    def _compute_hash(self, key):
        return hmac.new(
            key.encode(),
            json.dumps(self.data, sort_keys=True).encode(),
            hashlib.sha256
        ).hexdigest()

    def verify_integrity(self, key):
        return hmac.compare_digest(
            self.integrity_hash,
            self._compute_hash(key)
        )
```

## Person or Entity Authentication (§164.312(d))

### Requirements
- Verify identity before accessing ePHI
- MFA recommended for remote access
- Strong authentication mechanisms

```python
# Example: Multi-factor authentication for ePHI access
def authenticate_for_phi_access(user, password, mfa_token=None):
    """Authenticate user for ePHI access."""
    # Primary authentication
    if not verify_password(password, user.password_hash):
        audit_log.record("AUTH_FAILED", user.id, "invalid_password")
        raise AuthenticationError()

    # MFA required for remote access or sensitive operations
    if requires_mfa(user, request):
        if not mfa_token or not verify_mfa(user, mfa_token):
            audit_log.record("AUTH_FAILED", user.id, "invalid_mfa")
            raise MFARequiredError()

    audit_log.record("AUTH_SUCCESS", user.id)
    return create_phi_session(user)
```

## Transmission Security (§164.312(e))

### Integrity Controls (Addressable)
**Implementation:**
- TLS 1.2+ for all ePHI transmission
- Verify data not modified in transit
- Certificate validation

### Encryption (Addressable)
**Implementation:**
- Encrypt ePHI during electronic transmission
- Use approved encryption (AES-256, RSA 2048+)

```python
# Example: Secure API endpoint for PHI
@app.route('/api/patient/<patient_id>')
@require_tls
@require_authentication
@audit_access
def get_patient(patient_id):
    """Secure endpoint for patient data."""
    # Verify caller is authorized
    if not current_user.can_access_patient(patient_id):
        audit_log.record("UNAUTHORIZED_PHI_ACCESS", current_user.id, patient_id)
        return {"error": "Unauthorized"}, 403

    patient = Patient.query.get_or_404(patient_id)
    return patient.to_dict(role=current_user.role)  # Role-based data filtering
```

## De-identification

### Safe Harbor Method
Remove these 18 identifiers:
1. Names
2. Geographic data (smaller than state)
3. Dates (except year) related to individual
4. Phone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers
13. Device identifiers
14. Web URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photos
18. Any unique identifying number

```python
def deidentify_record(record):
    """De-identify a patient record using Safe Harbor method."""
    deidentified = record.copy()

    # Remove direct identifiers
    fields_to_remove = [
        'name', 'ssn', 'phone', 'email', 'address',
        'mrn', 'account_number', 'ip_address'
    ]
    for field in fields_to_remove:
        deidentified.pop(field, None)

    # Generalize dates to year only
    if 'birth_date' in deidentified:
        year = deidentified['birth_date'].year
        if year > datetime.now().year - 90:  # > 89 years old
            deidentified['birth_date'] = 'Over 89'
        else:
            deidentified['birth_date'] = str(year)

    # Generalize zip to 3 digits (if population > 20k)
    if 'zip_code' in deidentified:
        deidentified['zip_code'] = deidentified['zip_code'][:3] + '00'

    return deidentified
```

## Business Associate Requirements

### Code Considerations
- Verify BA agreements before data sharing
- Log all data transmissions to BAs
- Implement access controls for BA access
- Track data disclosed to each BA
