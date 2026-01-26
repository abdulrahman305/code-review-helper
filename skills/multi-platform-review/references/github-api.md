# GitHub PR API Reference

## Authentication

### Using gh CLI (Recommended)
```bash
gh auth login
# or
export GITHUB_TOKEN="ghp_xxxx"
```

### Token Permissions Required
- `repo` - Full repository access (for private repos)
- `public_repo` - Public repository access only
- `read:org` - For organization repositories

## Common Operations

### View PR Details
```bash
gh pr view {number} --repo {owner}/{repo}

# With JSON output
gh pr view {number} --json number,title,body,state,author,files,commits,reviews
```

### Get PR Diff
```bash
gh pr diff {number} --repo {owner}/{repo}
```

### List PR Files
```bash
gh pr view {number} --json files --jq '.files[].path'
```

### Get PR Comments
```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments
```

### Get PR Reviews
```bash
gh api repos/{owner}/{repo}/pulls/{number}/reviews
```

## API Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Get PR | GET | `/repos/{owner}/{repo}/pulls/{number}` |
| List files | GET | `/repos/{owner}/{repo}/pulls/{number}/files` |
| Get diff | GET | `/repos/{owner}/{repo}/pulls/{number}` (Accept: application/vnd.github.diff) |
| List commits | GET | `/repos/{owner}/{repo}/pulls/{number}/commits` |
| List comments | GET | `/repos/{owner}/{repo}/pulls/{number}/comments` |
| List reviews | GET | `/repos/{owner}/{repo}/pulls/{number}/reviews` |

## Response Fields

### PR Object
```json
{
  "number": 123,
  "title": "PR Title",
  "body": "Description",
  "state": "open",
  "user": {"login": "author"},
  "base": {"ref": "main"},
  "head": {"ref": "feature-branch"},
  "mergeable": true,
  "additions": 100,
  "deletions": 50,
  "changed_files": 5
}
```

### File Object
```json
{
  "sha": "abc123",
  "filename": "src/file.py",
  "status": "modified",
  "additions": 10,
  "deletions": 5,
  "changes": 15,
  "patch": "diff content"
}
```

## Rate Limits
- Authenticated: 5,000 requests/hour
- Unauthenticated: 60 requests/hour
- Check with: `gh api rate_limit`
