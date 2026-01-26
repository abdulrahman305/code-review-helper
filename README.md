# Code Review Helper

A comprehensive code review plugin for Claude Code with compliance auditing, security analysis, and multi-platform support.

## Features

- **Multi-Platform Support**: Review PRs from GitHub, GitLab, and Bitbucket
- **Compliance Frameworks**: NIST, FedRAMP, SOC 2, ISO 27001, HIPAA, PCI-DSS
- **Security Analysis**: Vulnerability detection, secret scanning, OWASP checks
- **Audit Reports**: Generate formal compliance reports in Markdown and JSON
- **Proactive Review**: Automatic code review suggestions after edits

## Components

### Commands

| Command | Description |
|---------|-------------|
| `/review-pr` | Review a pull request by URL (auto-detects platform) |
| `/review-file` | Full review of specified files |
| `/review-diff` | Review staged changes or git diff |
| `/compliance-check` | Run compliance-specific checks |
| `/audit-report` | Generate formal audit report |

### Agents

- **code-reviewer**: Comprehensive autonomous code review
- **compliance-auditor**: Specialized regulatory compliance checks

### Skills

- **code-review-practices**: Best practices for code quality and performance
- **compliance-frameworks**: Full control mappings for major frameworks
- **multi-platform-review**: GitHub, GitLab, Bitbucket integration patterns

## Installation

```bash
# Option 1: Use with --plugin-dir
claude --plugin-dir /path/to/code-review-helper

# Option 2: Copy to plugins folder
cp -r code-review-helper ~/.claude/plugins/
```

## Configuration

Create `.claude/code-review-helper.local.md` in your project:

```yaml
---
frameworks:
  - NIST
  - SOC2
  - HIPAA
severity_threshold: medium
platforms:
  github:
    token_env: GITHUB_TOKEN
  gitlab:
    token_env: GITLAB_TOKEN
  bitbucket:
    token_env: BITBUCKET_TOKEN
---

## Custom Rules

Add project-specific compliance rules here.
```

## Severity Levels

Findings use a 5-tier classification:

1. **Critical**: Must fix immediately (security vulnerabilities, data exposure)
2. **High**: Should fix before merge (significant issues)
3. **Medium**: Recommended to fix (code quality concerns)
4. **Low**: Consider fixing (minor improvements)
5. **Informational**: FYI only (style suggestions, notes)

## Environment Variables

Set platform tokens for PR review functionality:

```bash
export GITHUB_TOKEN="your_github_token"
export GITLAB_TOKEN="your_gitlab_token"
export BITBUCKET_TOKEN="your_bitbucket_token"
```

## License

MIT
