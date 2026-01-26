# Bitbucket PR API Reference

## Authentication

### App Password Setup
1. Go to Bitbucket Settings → App passwords
2. Create password with permissions:
   - Repositories: Read
   - Pull requests: Read

```bash
export BITBUCKET_USERNAME="your_username"
export BITBUCKET_APP_PASSWORD="xxxx"
```

### Using curl
```bash
curl -u "$BITBUCKET_USERNAME:$BITBUCKET_APP_PASSWORD" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{id}"
```

## API Base URL
```
https://api.bitbucket.org/2.0
```

## Common Operations

### Get PR Details
```bash
curl -u "$AUTH" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{id}"
```

### Get PR Diff
```bash
curl -u "$AUTH" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{id}/diff"
```

### Get PR Diffstat (file changes)
```bash
curl -u "$AUTH" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{id}/diffstat"
```

### Get PR Commits
```bash
curl -u "$AUTH" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{id}/commits"
```

## API Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Get PR | GET | `/repositories/{workspace}/{repo}/pullrequests/{id}` |
| Get diff | GET | `/repositories/{workspace}/{repo}/pullrequests/{id}/diff` |
| Get diffstat | GET | `/repositories/{workspace}/{repo}/pullrequests/{id}/diffstat` |
| Get commits | GET | `/repositories/{workspace}/{repo}/pullrequests/{id}/commits` |
| Get comments | GET | `/repositories/{workspace}/{repo}/pullrequests/{id}/comments` |
| Get activity | GET | `/repositories/{workspace}/{repo}/pullrequests/{id}/activity` |

## Response Fields

### PR Object
```json
{
  "id": 67,
  "title": "PR Title",
  "description": "Description",
  "state": "OPEN",
  "author": {
    "display_name": "Author Name",
    "account_id": "xxx"
  },
  "source": {
    "branch": {"name": "feature"}
  },
  "destination": {
    "branch": {"name": "main"}
  },
  "merge_commit": null,
  "close_source_branch": true
}
```

### Diffstat Object
```json
{
  "values": [
    {
      "type": "diffstat",
      "status": "modified",
      "lines_added": 10,
      "lines_removed": 5,
      "old": {"path": "src/file.py"},
      "new": {"path": "src/file.py"}
    }
  ]
}
```

### Status Values
- `modified` - File changed
- `added` - New file
- `removed` - File deleted
- `renamed` - File renamed

## Pagination

Bitbucket uses cursor-based pagination:
```json
{
  "values": [...],
  "next": "https://api.bitbucket.org/2.0/...?page=2",
  "previous": null,
  "page": 1,
  "size": 10
}
```

Follow the `next` URL to get more results.

## Rate Limits
- Authenticated: 1,000 requests/hour
- Check headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`
