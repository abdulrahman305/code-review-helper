# Security Review Checklist

## Input Validation

### All Languages
- [ ] All external input validated before use
- [ ] Validation uses allowlists, not denylists
- [ ] Input length limits enforced
- [ ] Character encoding normalized
- [ ] Multipart/file uploads validated (type, size, name)

### Web Applications
- [ ] Request parameters validated and sanitized
- [ ] File uploads restricted by type and size
- [ ] Rate limiting on endpoints
- [ ] CORS configured correctly

### APIs
- [ ] Request body validated against schema
- [ ] Query parameters typed and bounded
- [ ] Headers validated where used
- [ ] Pagination limits enforced

## Injection Prevention

### SQL Injection
```python
# VULNERABLE
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# SAFE - Parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### Command Injection
```python
# VULNERABLE
os.system(f"convert {filename} output.png")

# SAFE - Use subprocess with list arguments
subprocess.run(["convert", filename, "output.png"])
```

### XSS Prevention
```javascript
// VULNERABLE - Direct HTML insertion
element.innerHTML = userInput;

// SAFE - Text content or sanitized HTML
element.textContent = userInput;
// or use DOMPurify for HTML
element.innerHTML = DOMPurify.sanitize(userInput);
```

### Path Traversal
```python
# VULNERABLE
path = f"/uploads/{filename}"
return send_file(path)

# SAFE - Validate path stays within directory
import os
base_dir = "/uploads"
requested_path = os.path.realpath(os.path.join(base_dir, filename))
if not requested_path.startswith(os.path.realpath(base_dir)):
    raise SecurityError("Path traversal detected")
```

## Authentication

### Password Handling
- [ ] Passwords hashed with bcrypt/argon2 (not MD5/SHA1)
- [ ] Password requirements enforced (length, complexity)
- [ ] Brute force protection (lockout, delays)
- [ ] Password reset tokens single-use and time-limited
- [ ] Old password required for password changes

### Session Management
- [ ] Session IDs are random and unpredictable
- [ ] Sessions invalidated on logout
- [ ] Session timeout implemented
- [ ] Session fixation prevented (regenerate on login)
- [ ] Concurrent session limits where appropriate

### Token Handling (JWT/OAuth)
- [ ] Tokens have appropriate expiration
- [ ] Refresh token rotation implemented
- [ ] Signature algorithm hardcoded (not from token)
- [ ] Token revocation mechanism exists
- [ ] Sensitive claims not in JWT payload

## Authorization

### Access Control
- [ ] Authorization checked on every request
- [ ] Default deny policy
- [ ] IDOR (Insecure Direct Object Reference) prevented
- [ ] Privilege escalation paths reviewed
- [ ] Admin functions properly protected

### IDOR Prevention
```python
# VULNERABLE - User can access any document by ID
@app.route("/documents/<doc_id>")
def get_document(doc_id):
    return Document.query.get(doc_id)

# SAFE - Verify ownership
@app.route("/documents/<doc_id>")
def get_document(doc_id):
    doc = Document.query.get(doc_id)
    if doc.owner_id != current_user.id:
        raise Forbidden()
    return doc
```

## Data Protection

### Sensitive Data Handling
- [ ] PII encrypted at rest
- [ ] Sensitive data not logged
- [ ] Error messages don't expose internals
- [ ] Debug mode disabled in production
- [ ] Sensitive data masked in UI (SSN: ***-**-1234)

### Secrets Management
- [ ] No hardcoded credentials in code
- [ ] Secrets loaded from environment/vault
- [ ] API keys not in client-side code
- [ ] Git history checked for committed secrets
- [ ] Different credentials per environment

### Encryption
- [ ] TLS 1.2+ for all connections
- [ ] Strong cipher suites only
- [ ] Certificate validation enabled
- [ ] Encryption keys properly managed
- [ ] PII encrypted with AES-256 or equivalent

## Language-Specific

### JavaScript/Node.js
- [ ] npm packages audited (`npm audit`)
- [ ] eval() not used with user input
- [ ] Object prototype pollution prevented
- [ ] Content-Security-Policy headers set
- [ ] __proto__ assignments blocked

### Python
- [ ] pickle not used with untrusted data
- [ ] yaml.safe_load() used (not yaml.load())
- [ ] subprocess.shell=False with user input
- [ ] format strings don't use user input as format
- [ ] Dependencies audited (`safety check`)

### Go
- [ ] Integer overflow checks where needed
- [ ] html/template used for HTML output
- [ ] crypto/rand used (not math/rand) for security
- [ ] Race conditions checked (`go test -race`)

### Java
- [ ] XML parsers configured to prevent XXE
- [ ] Serialization disabled or filtered
- [ ] SQL queries use PreparedStatement
- [ ] Dependency vulnerabilities checked

## Common Vulnerabilities Reference

### OWASP Top 10 (2021)
1. A01 - Broken Access Control
2. A02 - Cryptographic Failures
3. A03 - Injection
4. A04 - Insecure Design
5. A05 - Security Misconfiguration
6. A06 - Vulnerable Components
7. A07 - Authentication Failures
8. A08 - Data Integrity Failures
9. A09 - Logging Failures
10. A10 - SSRF

### Secret Patterns to Scan
```regex
# AWS
AKIA[0-9A-Z]{16}

# GitHub
ghp_[a-zA-Z0-9]{36}
github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}

# Generic API Keys
[a-zA-Z0-9]{32,}

# Private Keys
-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----

# Passwords in URLs
://[^:]+:[^@]+@
```
