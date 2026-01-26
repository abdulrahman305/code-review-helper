---
name: Multi-Platform Review
description: This skill should be used when the user asks to "review a PR", "review GitHub pull request", "review GitLab merge request", "review Bitbucket PR", "fetch PR diff", "get MR changes", or when integrating with any code hosting platform for reviews. Provides patterns for GitHub, GitLab, and Bitbucket API integration.
version: 1.0.0
---

# Multi-Platform Review

Integration patterns for reviewing pull requests and merge requests across GitHub, GitLab, and Bitbucket.

## Overview

Review code changes from any major platform by detecting the platform from URL and using the appropriate API or CLI tool.

## Platform Detection

### URL Patterns

| Platform | URL Pattern | Example |
|----------|-------------|---------|
| GitHub | `github.com/{owner}/{repo}/pull/{number}` | `github.com/org/repo/pull/123` |
| GitLab | `gitlab.com/{path}/merge_requests/{number}` | `gitlab.com/group/repo/-/merge_requests/45` |
| Bitbucket | `bitbucket.org/{workspace}/{repo}/pull-requests/{number}` | `bitbucket.org/team/repo/pull-requests/67` |

### Detection Logic

```python
def detect_platform(url):
    if 'github.com' in url:
        return 'github'
    elif 'gitlab.com' in url or 'gitlab' in url:
        return 'gitlab'
    elif 'bitbucket.org' in url:
        return 'bitbucket'
    return None
```

## GitHub Integration

### Using gh CLI (Recommended)

The `gh` CLI provides the simplest integration for GitHub:

```bash
# View PR details
gh pr view 123

# Get PR diff
gh pr diff 123

# View PR files changed
gh pr view 123 --json files

# Get PR comments
gh api repos/{owner}/{repo}/pulls/123/comments
```

### Required Environment

```bash
# Authenticate with GitHub
gh auth login

# Or use token
export GITHUB_TOKEN="your_token"
```

### Fetching PR Data

```bash
# Get comprehensive PR data as JSON
gh pr view 123 --json number,title,body,state,files,commits,reviews,comments

# Get diff content
gh pr diff 123
```

### Key API Endpoints

| Action | Command |
|--------|---------|
| PR Details | `gh pr view {number}` |
| PR Diff | `gh pr diff {number}` |
| List Files | `gh pr view {number} --json files` |
| Comments | `gh api repos/{owner}/{repo}/pulls/{number}/comments` |
| Reviews | `gh api repos/{owner}/{repo}/pulls/{number}/reviews` |
| Commits | `gh pr view {number} --json commits` |

## GitLab Integration

### Using glab CLI

GitLab offers the `glab` CLI for similar functionality:

```bash
# View MR details
glab mr view 45

# Get MR diff
glab mr diff 45

# View MR changes
glab api projects/:id/merge_requests/45/changes
```

### API Access

```bash
# Set token
export GITLAB_TOKEN="your_token"

# API request
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/{id}/merge_requests/{mr_iid}/changes"
```

### Key API Endpoints

| Action | Endpoint |
|--------|----------|
| MR Details | `GET /projects/:id/merge_requests/:mr_iid` |
| MR Changes | `GET /projects/:id/merge_requests/:mr_iid/changes` |
| MR Commits | `GET /projects/:id/merge_requests/:mr_iid/commits` |
| MR Notes | `GET /projects/:id/merge_requests/:mr_iid/notes` |
| MR Diffs | `GET /projects/:id/merge_requests/:mr_iid/diffs` |

### Project ID Resolution

GitLab requires project ID, which can be URL-encoded path:

```bash
# Using URL-encoded project path
curl "https://gitlab.com/api/v4/projects/group%2Frepo/merge_requests/45"
```

## Bitbucket Integration

### API Access

```bash
# Set credentials
export BITBUCKET_USERNAME="your_username"
export BITBUCKET_APP_PASSWORD="your_app_password"

# API request
curl -u "$BITBUCKET_USERNAME:$BITBUCKET_APP_PASSWORD" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{id}"
```

### Key API Endpoints

| Action | Endpoint |
|--------|----------|
| PR Details | `GET /repositories/{workspace}/{repo}/pullrequests/{id}` |
| PR Diff | `GET /repositories/{workspace}/{repo}/pullrequests/{id}/diff` |
| PR Commits | `GET /repositories/{workspace}/{repo}/pullrequests/{id}/commits` |
| PR Comments | `GET /repositories/{workspace}/{repo}/pullrequests/{id}/comments` |

## Unified Review Workflow

### 1. Parse URL and Detect Platform

```python
import re

def parse_pr_url(url):
    patterns = {
        'github': r'github\.com/([^/]+)/([^/]+)/pull/(\d+)',
        'gitlab': r'gitlab\.com/(.+)/-/merge_requests/(\d+)',
        'bitbucket': r'bitbucket\.org/([^/]+)/([^/]+)/pull-requests/(\d+)'
    }

    for platform, pattern in patterns.items():
        match = re.search(pattern, url)
        if match:
            return {
                'platform': platform,
                'groups': match.groups()
            }
    return None
```

### 2. Fetch PR/MR Data

Based on detected platform, use the appropriate CLI or API:

**GitHub:**
```bash
gh pr view "$PR_NUMBER" --json title,body,files,commits
gh pr diff "$PR_NUMBER"
```

**GitLab:**
```bash
glab mr view "$MR_NUMBER"
glab api "projects/$PROJECT_ID/merge_requests/$MR_NUMBER/changes"
```

**Bitbucket:**
```bash
curl -u "$BITBUCKET_AUTH" \
  "https://api.bitbucket.org/2.0/repositories/$WORKSPACE/$REPO/pullrequests/$PR_ID/diff"
```

### 3. Normalize Data Format

Convert platform-specific data to unified format:

```python
unified_pr = {
    "platform": "github|gitlab|bitbucket",
    "number": 123,
    "title": "PR Title",
    "description": "PR description",
    "author": "username",
    "state": "open|merged|closed",
    "files_changed": [
        {
            "path": "src/file.py",
            "additions": 10,
            "deletions": 5,
            "status": "modified|added|deleted"
        }
    ],
    "diff": "unified diff content",
    "commits": [
        {
            "sha": "abc123",
            "message": "Commit message"
        }
    ]
}
```

## Environment Configuration

### Required Tokens

Store tokens in environment variables:

```bash
# GitHub
export GITHUB_TOKEN="ghp_xxxx"

# GitLab
export GITLAB_TOKEN="glpat-xxxx"

# Bitbucket (use App Password, not account password)
export BITBUCKET_USERNAME="username"
export BITBUCKET_APP_PASSWORD="xxxx"
```

### Token Permissions

**GitHub:**
- `repo` - Full repository access
- `read:org` - For organization repos

**GitLab:**
- `read_api` - Read API access
- `read_repository` - Read repository contents

**Bitbucket:**
- `Repositories: Read`
- `Pull requests: Read`

## Utility Scripts

### PR Fetcher

Use `${CLAUDE_PLUGIN_ROOT}/skills/multi-platform-review/scripts/fetch-pr.py` to fetch PR data:

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/multi-platform-review/scripts/fetch-pr.py <url>
```

## Additional Resources

### Reference Files

For detailed API documentation:
- **`references/github-api.md`** - GitHub PR API details
- **`references/gitlab-api.md`** - GitLab MR API details
- **`references/bitbucket-api.md`** - Bitbucket PR API details

## Error Handling

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid/missing token | Check token and permissions |
| 404 Not Found | Wrong URL or private repo | Verify URL and access |
| 403 Forbidden | Rate limit or no access | Check rate limits, verify permissions |
| SSL Error | Network/proxy issue | Check network settings |

### Rate Limits

| Platform | Limit | Reset |
|----------|-------|-------|
| GitHub | 5000/hour (authenticated) | Hourly |
| GitLab | 2000/minute | Per minute |
| Bitbucket | 1000/hour | Hourly |
