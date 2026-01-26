# NIST 800-53 Code-Relevant Controls

## Access Control (AC)

### AC-2 Account Management
**Code Requirements:**
- User registration with approval workflow
- Account disable/enable functionality
- Automatic deactivation for inactive accounts
- Role assignment auditing

```python
# Example: Account management with audit
class AccountManager:
    def create_account(self, user_data, approver_id):
        if not self.validate_approval(approver_id):
            raise UnauthorizedError("Approval required")
        user = User.create(user_data)
        audit_log.record("ACCOUNT_CREATED", user.id, approver_id)
        return user

    def deactivate_inactive_accounts(self, days=90):
        inactive = User.query.filter(
            User.last_login < datetime.now() - timedelta(days=days)
        )
        for user in inactive:
            user.status = "inactive"
            audit_log.record("ACCOUNT_DEACTIVATED", user.id, "SYSTEM")
```

### AC-3 Access Enforcement
**Code Requirements:**
- Authorization check on every request
- Deny by default policy
- Resource-level access control

```python
# Example: Authorization decorator
def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.has_permission(permission):
                audit_log.record("ACCESS_DENIED", current_user.id, permission)
                raise ForbiddenError()
            return f(*args, **kwargs)
        return wrapped
    return decorator
```

### AC-6 Least Privilege
**Code Requirements:**
- Minimal default permissions
- Privilege escalation requires justification
- Time-limited elevated access

### AC-7 Unsuccessful Logon Attempts
**Code Requirements:**
- Track failed login attempts
- Account lockout after threshold (typically 3-5 attempts)
- Lockout duration or admin unlock required

```python
# Example: Login attempt tracking
def authenticate(username, password):
    user = User.get(username)
    if user.locked_until and user.locked_until > datetime.now():
        raise AccountLockedError()

    if not verify_password(password, user.password_hash):
        user.failed_attempts += 1
        if user.failed_attempts >= MAX_ATTEMPTS:
            user.locked_until = datetime.now() + timedelta(minutes=30)
        audit_log.record("LOGIN_FAILED", username)
        raise AuthenticationError()

    user.failed_attempts = 0
    audit_log.record("LOGIN_SUCCESS", username)
    return create_session(user)
```

## Audit and Accountability (AU)

### AU-2 Audit Events
**Required Events:**
- Successful and unsuccessful login attempts
- Privilege escalation
- Access to sensitive data
- System configuration changes
- Account management actions
- Security-relevant application events

### AU-3 Content of Audit Records
**Required Fields:**
```python
audit_record = {
    "timestamp": datetime.utcnow().isoformat(),
    "event_type": "DATA_ACCESS",
    "user_id": current_user.id,
    "user_ip": request.remote_addr,
    "resource": "/api/patients/12345",
    "action": "READ",
    "outcome": "SUCCESS",
    "session_id": session.id,
    "additional_info": {}
}
```

### AU-9 Protection of Audit Information
**Code Requirements:**
- Audit logs append-only
- Separate storage from application data
- Integrity verification (hashing, signing)
- Access to audit logs restricted and logged

### AU-12 Audit Generation
**Code Requirements:**
- Automatic audit record generation
- Time synchronization (NTP)
- Consistent format across components

## Identification and Authentication (IA)

### IA-2 Identification and Authentication
**Code Requirements:**
- Unique user identifiers
- Multi-factor authentication for privileged access
- Network access authentication

### IA-5 Authenticator Management
**Password Requirements:**
- Minimum 12 characters (FedRAMP High: 15)
- Complexity (upper, lower, number, special)
- Password history (prevent reuse of last 24)
- 60-day maximum lifetime

```python
# Example: Password validation
def validate_password(password, user_history):
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain uppercase")
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain lowercase")
    if not re.search(r'[0-9]', password):
        raise ValueError("Password must contain number")
    if not re.search(r'[!@#$%^&*]', password):
        raise ValueError("Password must contain special character")

    # Check history
    for old_hash in user_history[-24:]:
        if verify_password(password, old_hash):
            raise ValueError("Password used recently")
```

**Hashing Requirements:**
- Use bcrypt, scrypt, or PBKDF2
- Minimum work factor (bcrypt: 12+)
- Unique salt per password

## System and Communications Protection (SC)

### SC-8 Transmission Confidentiality
**Code Requirements:**
- TLS 1.2 or higher
- Strong cipher suites only
- Certificate validation
- HSTS headers

```python
# Example: TLS configuration
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
ssl_context.set_ciphers('ECDHE+AESGCM:DHE+AESGCM:ECDHE+CHACHA20')
```

### SC-13 Cryptographic Protection
**FIPS 140-2 Approved Algorithms:**
- AES (128, 192, 256 bit)
- SHA-2 family (SHA-256, SHA-384, SHA-512)
- RSA (2048+ bit)
- ECDSA (P-256, P-384)

**Non-Compliant (avoid):**
- DES, 3DES, RC4
- MD5, SHA-1 (for security)
- RSA < 2048 bit

### SC-28 Protection of Information at Rest
**Code Requirements:**
- Encrypt sensitive data at rest
- Key management separate from data
- Secure key storage (HSM, key vault)

```python
# Example: Field-level encryption
from cryptography.fernet import Fernet

class EncryptedField:
    def __init__(self, key_provider):
        self.key_provider = key_provider

    def encrypt(self, value):
        key = self.key_provider.get_current_key()
        f = Fernet(key)
        return f.encrypt(value.encode())

    def decrypt(self, encrypted_value):
        key = self.key_provider.get_key_for_data(encrypted_value)
        f = Fernet(key)
        return f.decrypt(encrypted_value).decode()
```

## System and Information Integrity (SI)

### SI-10 Information Input Validation
**Code Requirements:**
- Validate all external input
- Check syntax and semantics
- Whitelist validation preferred
- Reject invalid input (don't sanitize)

```python
# Example: Input validation
from pydantic import BaseModel, validator, constr

class UserInput(BaseModel):
    username: constr(min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    age: int

    @validator('age')
    def validate_age(cls, v):
        if not 0 <= v <= 150:
            raise ValueError('Invalid age')
        return v
```

### SI-11 Error Handling
**Code Requirements:**
- Generic error messages to users
- Detailed logging for debugging
- No stack traces in production responses
- Graceful degradation

```python
# Example: Secure error handling
@app.errorhandler(Exception)
def handle_error(error):
    error_id = generate_error_id()
    logger.error(f"Error {error_id}: {error}", exc_info=True)

    if isinstance(error, ValidationError):
        return {"error": "Invalid input", "error_id": error_id}, 400
    else:
        return {"error": "Internal error", "error_id": error_id}, 500
```

## Configuration Management (CM)

### CM-7 Least Functionality
**Code Requirements:**
- Disable unnecessary features
- Remove debug endpoints in production
- Minimal dependencies
- No default/sample credentials

### CM-8 Information System Component Inventory
**Code Requirements:**
- Dependency tracking (package.json, requirements.txt)
- Software bill of materials (SBOM)
- Version documentation
