# GitLab MR API Reference

## Authentication

### Token Setup
```bash
export GITLAB_TOKEN="glpat-xxxx"
```

### Token Scopes Required
- `read_api` - Read API access
- `read_repository` - Read repository contents

## Common Operations

### Using glab CLI
```bash
# Install glab
brew install glab  # macOS
# or
snap install glab  # Linux

# Authenticate
glab auth login

# View MR
glab mr view {number}

# Get MR diff
glab mr diff {number}
```

### Using curl
```bash
# Get MR details
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_iid}"

# Get MR changes
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_iid}/changes"
```

## Project ID

GitLab requires a project ID, which can be:
- Numeric ID: `12345678`
- URL-encoded path: `group%2Fsubgroup%2Fproject`

```bash
# Get project ID from path
curl -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/group%2Fproject" | jq '.id'
```

## API Endpoints

| Action | Method | Endpoint |
|--------|--------|----------|
| Get MR | GET | `/projects/:id/merge_requests/:mr_iid` |
| Get changes | GET | `/projects/:id/merge_requests/:mr_iid/changes` |
| Get commits | GET | `/projects/:id/merge_requests/:mr_iid/commits` |
| Get diffs | GET | `/projects/:id/merge_requests/:mr_iid/diffs` |
| Get notes | GET | `/projects/:id/merge_requests/:mr_iid/notes` |
| Get discussions | GET | `/projects/:id/merge_requests/:mr_iid/discussions` |

## Response Fields

### MR Object
```json
{
  "iid": 45,
  "title": "MR Title",
  "description": "Description",
  "state": "opened",
  "author": {"username": "author"},
  "source_branch": "feature",
  "target_branch": "main",
  "merge_status": "can_be_merged",
  "changes_count": "5"
}
```

### Change Object
```json
{
  "old_path": "src/old.py",
  "new_path": "src/new.py",
  "new_file": false,
  "renamed_file": true,
  "deleted_file": false,
  "diff": "diff content"
}
```

## Rate Limits
- Authenticated: 2,000 requests/minute
- Check with: `curl -I -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "https://gitlab.com/api/v4/projects"`
