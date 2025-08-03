# Security Considerations for AI News Summarizer

## Overview

This document outlines the security measures implemented in the AI News Summarizer and provides best practices for secure deployment and operation.

## Security Features Implemented

### 1. Input Validation and Sanitization

#### URL Validation
- **SSRF Prevention**: All URLs are validated before fetching
- **Blocked Domains**: Local addresses (localhost, 127.0.0.1, GCP metadata endpoint) are blocked
- **Scheme Validation**: Only HTTP/HTTPS schemes are allowed
- **IP Address Blocking**: Direct IP addresses are not allowed

```python
# Example: URL validation in web_scraper.py
clean_url = validate_url(url)
if not clean_url:
    logger.warning(f"Invalid or blocked URL: {url}")
    return None
```

#### Content Size Limits
- Maximum content size: 10MB to prevent memory exhaustion
- Streaming content with chunk validation
- Early termination for oversized content

#### Data Sanitization
- All data sent to Slack is HTML-escaped
- Control characters are removed
- Content length is limited to prevent oversized messages

### 2. Secret Management

#### Environment Variables
- All sensitive data stored in environment variables
- No hardcoded credentials in source code
- Google Cloud Functions environment variables encrypted at rest

#### Required Secrets
- `OPENROUTER_API_KEY`: API key for LLM access
- `SLACK_WEBHOOK_URL`: Webhook for Slack integration

### 3. Logging Security

#### Sensitive Data Redaction
- Custom logging formatter sanitizes logs
- API keys, passwords, and tokens are automatically redacted
- URLs with credentials are sanitized

```python
# Example redacted log output
Original: api_key=sk-1234567890abcdef
Logged: api_key=[REDACTED]
```

#### Cloud Logging Integration
- Logs retention set to 30 days
- No sensitive data persisted in logs

### 4. Network Security

#### Request Timeouts
- All HTTP requests have 30-second timeout
- Prevents hanging connections
- Graceful failure handling

#### TLS/SSL
- All external communications use HTTPS
- Certificate validation enabled by default

### 5. Error Handling

#### Specific Exception Handling
- Firestore throttling with exponential backoff
- Network errors with retry logic
- API rate limiting handled gracefully

#### Fail-Safe Defaults
- Errors default to safe behavior (e.g., URL treated as unprocessed)
- No sensitive information in error messages

### 6. GCP Security

#### IAM Permissions
- Least privilege principle
- Cloud Function service account only has required permissions:
  - Firestore read/write to specific collection
  - Cloud Logging creation
  - No cross-project access

#### Firestore Security
- Encryption at rest enabled
- Automatic scaling (no over-provisioning)
- TTL policies for automatic data cleanup

## Deployment Security Checklist

### Pre-Deployment

- [ ] Verify all dependencies are from trusted sources
- [ ] Run security scanning tools (e.g., `safety check`)
- [ ] Review deployment configuration for excessive permissions
- [ ] Ensure secrets are stored in Google Secret Manager
- [ ] Enable Cloud Audit Logs for audit logging

### Environment Variables

```bash
# Never commit .env files
echo ".env" >> .gitignore

# Use Google Secret Manager
gcloud secrets create ai-news-summarizer-openrouter \
  --data-file=- <<< "your-api-key"
```

### Network Configuration

- [ ] Cloud Functions with VPC connector (if required)
- [ ] Firewall rules with minimal ingress
- [ ] No public IP assignment
- [ ] Private Google Access for GCP services

## Security Best Practices

### 1. Regular Updates

```bash
# Check for vulnerable dependencies
pip install safety
safety check -r requirements.txt

# Update dependencies
pip install --upgrade -r requirements.txt
```

### 2. API Key Rotation

- Rotate OpenRouter API key quarterly
- Update Slack webhook if compromised
- Use Google Secret Manager rotation feature

### 3. Monitoring and Alerting

#### Cloud Monitoring Alerts
- Cloud Function errors > threshold
- Unusual Firestore activity
- Failed authentication attempts

#### Security Metrics
- Track processed URLs for anomalies
- Monitor Cloud Function invocation patterns
- Alert on configuration changes

### 4. Incident Response

#### If API Key Compromised
1. Immediately rotate the key
2. Update Cloud Function environment variables
3. Review Cloud Logging for unauthorized usage
4. Report to OpenRouter if suspicious activity

#### If Slack Webhook Compromised
1. Regenerate webhook in Slack
2. Update Cloud Function configuration
3. Review Slack channel for unauthorized posts

## Compliance Considerations

### Data Privacy
- No PII collected or stored
- Only public RSS feed data processed
- Processed URLs stored with 90-day TTL

### Audit Trail
- All Cloud Function invocations logged
- Firestore operations tracked
- Cloud Audit Logs enabled for GCP API calls

## Security Testing

### Static Analysis
```bash
# Run bandit for security issues
pip install bandit
bandit -r src/

# Check for hardcoded secrets
grep -r "api_key\|password\|secret" src/
```

### Dependency Scanning
```bash
# Check for known vulnerabilities
pip install pip-audit
pip-audit

# Generate dependency report
pip freeze > dependencies.txt
```

## Vulnerability Reporting

If you discover a security vulnerability:

1. Do NOT open a public issue
2. Email security concerns to: [your-security-email]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Updates

This document is maintained alongside the codebase. Security patches are prioritized and released as soon as possible.

Last reviewed: 2024-01-10
Next review: 2024-04-10