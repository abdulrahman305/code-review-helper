# PCI-DSS Code Requirements

## Overview

PCI-DSS (Payment Card Industry Data Security Standard) applies to any entity that stores, processes, or transmits cardholder data (CHD) or sensitive authentication data (SAD).

## Cardholder Data Elements

### What Must Be Protected

| Data Element | Storage Permitted | Protection Required |
|--------------|-------------------|---------------------|
| Primary Account Number (PAN) | Yes | Render unreadable |
| Cardholder Name | Yes | Protection required |
| Service Code | Yes | Protection required |
| Expiration Date | Yes | Protection required |
| Full Magnetic Stripe | **No** | Never store post-auth |
| CAV2/CVC2/CVV2/CID | **No** | Never store post-auth |
| PIN/PIN Block | **No** | Never store post-auth |

### PAN Handling

```python
# NEVER: Store full PAN in logs
logger.info(f"Processing card {card_number}")  # VIOLATION!

# CORRECT: Mask PAN for logging
def mask_pan(pan):
    """Mask PAN showing only first 6 and last 4 digits."""
    if len(pan) < 13:
        return "INVALID"
    return pan[:6] + "*" * (len(pan) - 10) + pan[-4:]

logger.info(f"Processing card {mask_pan(card_number)}")
# Output: Processing card 411111******1111
```

## Requirement 3: Protect Stored Cardholder Data

### 3.4 Render PAN Unreadable

Acceptable methods:
- Strong one-way hash (SHA-256 with salt)
- Truncation (first 6, last 4)
- Index tokens with secure lookup
- Strong cryptography with key management

```python
# Example: PAN tokenization
import secrets
import hashlib

class CardTokenizer:
    def __init__(self, token_vault):
        self.vault = token_vault

    def tokenize(self, pan):
        """Replace PAN with token for storage."""
        # Generate random token
        token = secrets.token_hex(16)

        # Store mapping securely (encrypted at rest)
        self.vault.store(token, self._encrypt_pan(pan))

        return token

    def detokenize(self, token, reason):
        """Retrieve PAN from token (audit logged)."""
        audit_log.record("PAN_DETOKENIZE", token=token, reason=reason)
        encrypted_pan = self.vault.retrieve(token)
        return self._decrypt_pan(encrypted_pan)
```

### 3.5 Key Management

```python
# Example: Encryption key management
class KeyManager:
    def __init__(self, hsm_connection):
        self.hsm = hsm_connection

    def get_encryption_key(self, purpose):
        """Retrieve key from HSM for specific purpose."""
        # Keys stored in HSM, never in code
        return self.hsm.get_key(purpose)

    def rotate_key(self, purpose):
        """Rotate encryption key."""
        new_key = self.hsm.generate_key(purpose)
        # Re-encrypt data with new key (scheduled job)
        return new_key

    def destroy_key(self, key_id):
        """Securely destroy key."""
        audit_log.record("KEY_DESTROYED", key_id)
        self.hsm.destroy_key(key_id)
```

## Requirement 4: Encrypt Transmission

### 4.1 Strong Cryptography for Transmission

```python
# Example: TLS configuration for payment APIs
import ssl

def create_secure_context():
    """Create TLS context meeting PCI requirements."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # TLS 1.2 minimum (1.3 preferred)
    context.minimum_version = ssl.TLSVersion.TLSv1_2

    # Strong cipher suites only
    context.set_ciphers(
        'ECDHE+AESGCM:'
        'DHE+AESGCM:'
        'ECDHE+CHACHA20:'
        '!aNULL:!MD5:!DSS:!RC4:!3DES'
    )

    # Load certificates
    context.load_cert_chain('server.crt', 'server.key')
    context.load_verify_locations('ca-bundle.crt')

    return context
```

## Requirement 6: Secure Systems and Software

### 6.5 Secure Coding Practices

Address common vulnerabilities:

#### 6.5.1 Injection Flaws

```python
# VULNERABLE: SQL injection
cursor.execute(f"SELECT * FROM cards WHERE pan = '{pan}'")

# SECURE: Parameterized query
cursor.execute("SELECT * FROM cards WHERE pan = %s", (pan,))
```

#### 6.5.4 Insecure Communications

```python
# VULNERABLE: HTTP for payment data
requests.post("http://payment.example.com/process", data=card_data)

# SECURE: HTTPS only
requests.post("https://payment.example.com/process", data=card_data, verify=True)
```

#### 6.5.6 Information Leakage

```python
# VULNERABLE: Exposing error details
@app.errorhandler(Exception)
def handle_error(e):
    return {"error": str(e), "stack": traceback.format_exc()}  # BAD!

# SECURE: Generic errors
@app.errorhandler(Exception)
def handle_error(e):
    error_id = log_error_details(e)  # Log internally
    return {"error": "An error occurred", "reference": error_id}
```

### 6.5.10 Broken Authentication

```python
# Example: Secure authentication for payment systems
class PaymentAuth:
    MAX_ATTEMPTS = 3
    LOCKOUT_MINUTES = 30

    def authenticate(self, user_id, password):
        user = User.get(user_id)

        # Check lockout
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise AccountLockedError()

        # Verify credentials
        if not self._verify_password(password, user.password_hash):
            self._handle_failed_attempt(user)
            raise AuthenticationError()

        # Reset on success
        user.failed_attempts = 0
        user.save()

        return self._create_session(user)

    def _handle_failed_attempt(self, user):
        user.failed_attempts += 1
        if user.failed_attempts >= self.MAX_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=self.LOCKOUT_MINUTES)
            audit_log.record("ACCOUNT_LOCKED", user.id)
        user.save()
```

## Requirement 8: Identify and Authenticate Access

### 8.2 Strong Authentication

```python
# Example: Password requirements
def validate_password(password):
    """PCI-DSS password requirements."""
    errors = []

    if len(password) < 7:  # 8.2.3: Minimum 7 characters
        errors.append("Password must be at least 7 characters")

    if not re.search(r'[A-Za-z]', password):
        errors.append("Password must contain letters")

    if not re.search(r'[0-9]', password):
        errors.append("Password must contain numbers")

    return errors

def check_password_history(user, new_password):
    """8.2.5: Cannot reuse last 4 passwords."""
    for old_hash in user.password_history[-4:]:
        if verify_password(new_password, old_hash):
            return False
    return True
```

### 8.3 MFA for Administrative Access

```python
# Example: MFA for CDE access
def access_cardholder_environment(user, password, mfa_code):
    """Require MFA for all CDE access."""
    # Standard authentication
    if not verify_password(password, user.password_hash):
        raise AuthenticationError()

    # MFA required for CDE
    if not verify_totp(user.mfa_secret, mfa_code):
        audit_log.record("MFA_FAILED", user.id)
        raise MFAError()

    audit_log.record("CDE_ACCESS_GRANTED", user.id)
    return create_cde_session(user)
```

## Requirement 10: Track and Monitor Access

### 10.2 Audit Trail Requirements

```python
# Required audit events for CDE
AUDIT_EVENTS = {
    "USER_ACCESS": "10.2.1 - Individual access to CHD",
    "ROOT_ACCESS": "10.2.2 - Actions by root/admin",
    "AUDIT_ACCESS": "10.2.3 - Access to audit trails",
    "INVALID_ACCESS": "10.2.4 - Invalid access attempts",
    "AUTH_MECHANISM": "10.2.5 - Auth mechanism changes",
    "AUDIT_INIT": "10.2.6 - Audit log initialization",
    "OBJECT_CHANGES": "10.2.7 - Creation/deletion of system objects"
}

def audit_chd_access(user, action, card_token, result):
    """Log all access to cardholder data."""
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user.id,
        "username": user.username,
        "action": action,
        "card_token": card_token,  # Never log actual PAN
        "result": result,
        "source_ip": request.remote_addr,
        "workstation": request.headers.get('X-Workstation-ID')
    }
    audit_log.write(record)
```

### 10.5 Secure Audit Trails

```python
# Example: Tamper-evident logging
import hashlib

class SecureAuditLog:
    def __init__(self, storage):
        self.storage = storage
        self.previous_hash = None

    def write(self, record):
        """Write tamper-evident audit record."""
        # Include hash of previous record for chain integrity
        record['previous_hash'] = self.previous_hash

        # Compute hash of this record
        record_json = json.dumps(record, sort_keys=True)
        record_hash = hashlib.sha256(record_json.encode()).hexdigest()
        record['record_hash'] = record_hash

        # Store record
        self.storage.append(record)
        self.previous_hash = record_hash

    def verify_integrity(self):
        """Verify audit log has not been tampered with."""
        records = self.storage.read_all()
        previous_hash = None

        for record in records:
            # Verify chain
            if record['previous_hash'] != previous_hash:
                return False, record

            # Verify record hash
            stored_hash = record.pop('record_hash')
            computed_hash = hashlib.sha256(
                json.dumps(record, sort_keys=True).encode()
            ).hexdigest()

            if stored_hash != computed_hash:
                return False, record

            previous_hash = stored_hash

        return True, None
```

## Requirement 11: Test Security Systems

### 11.3 Vulnerability Scanning

Code should support scanning:

```python
# Example: Expose version info for scanning (authorized scanners only)
@app.route('/version')
@require_internal_network
def version_info():
    """Return version info for vulnerability scanning."""
    return {
        "app_version": APP_VERSION,
        "dependencies": get_dependency_versions(),
        "os": platform.platform()
    }
```

## Data Flow Documentation

Document all CHD flows:

```
1. Card Entry → Input Validation → Tokenization
2. Token → Payment Processor (TLS 1.2+)
3. Response → Token Storage (encrypted)
4. Token → Display (masked: ****1234)
```
