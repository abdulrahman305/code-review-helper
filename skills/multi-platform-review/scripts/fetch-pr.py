#!/usr/bin/env python3
"""
Fetch pull request/merge request data from GitHub, GitLab, or Bitbucket.
Auto-detects platform from URL and fetches unified PR data.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class FileChange:
    path: str
    additions: int
    deletions: int
    status: str  # modified, added, deleted, renamed


@dataclass
class Commit:
    sha: str
    message: str
    author: str


@dataclass
class PullRequest:
    platform: str
    number: int
    title: str
    description: str
    author: str
    state: str
    base_branch: str
    head_branch: str
    files_changed: List[FileChange]
    commits: List[Commit]
    diff: str


def detect_platform(url: str) -> Optional[dict]:
    """Detect platform and extract info from URL."""
    patterns = {
        'github': (
            r'github\.com/([^/]+)/([^/]+)/pull/(\d+)',
            ['owner', 'repo', 'number']
        ),
        'gitlab': (
            r'gitlab\.com/(.+?)(?:/-)?/merge_requests/(\d+)',
            ['project', 'number']
        ),
        'bitbucket': (
            r'bitbucket\.org/([^/]+)/([^/]+)/pull-requests/(\d+)',
            ['workspace', 'repo', 'number']
        )
    }

    for platform, (pattern, fields) in patterns.items():
        match = re.search(pattern, url)
        if match:
            result = {'platform': platform}
            for i, field in enumerate(fields):
                result[field] = match.group(i + 1)
            return result

    return None


def run_command(cmd: List[str], check: bool = True) -> str:
    """Run a command and return output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        if check:
            raise
        return ""


def fetch_github_pr(owner: str, repo: str, number: str) -> PullRequest:
    """Fetch PR data from GitHub using gh CLI."""
    # Check if gh is available
    try:
        run_command(['gh', '--version'])
    except FileNotFoundError:
        print("Error: 'gh' CLI not found. Install from https://cli.github.com/", file=sys.stderr)
        sys.exit(1)

    # Fetch PR data
    pr_json = run_command([
        'gh', 'pr', 'view', number,
        '--repo', f'{owner}/{repo}',
        '--json', 'number,title,body,author,state,baseRefName,headRefName,files,commits'
    ])
    pr_data = json.loads(pr_json)

    # Fetch diff
    diff = run_command(['gh', 'pr', 'diff', number, '--repo', f'{owner}/{repo}'], check=False)

    # Parse files
    files = []
    for f in pr_data.get('files', []):
        files.append(FileChange(
            path=f.get('path', ''),
            additions=f.get('additions', 0),
            deletions=f.get('deletions', 0),
            status=f.get('status', 'modified').lower()
        ))

    # Parse commits
    commits = []
    for c in pr_data.get('commits', []):
        commits.append(Commit(
            sha=c.get('oid', '')[:8],
            message=c.get('messageHeadline', ''),
            author=c.get('authors', [{}])[0].get('login', '') if c.get('authors') else ''
        ))

    return PullRequest(
        platform='github',
        number=int(number),
        title=pr_data.get('title', ''),
        description=pr_data.get('body', ''),
        author=pr_data.get('author', {}).get('login', ''),
        state=pr_data.get('state', 'OPEN').lower(),
        base_branch=pr_data.get('baseRefName', ''),
        head_branch=pr_data.get('headRefName', ''),
        files_changed=files,
        commits=commits,
        diff=diff
    )


def fetch_gitlab_mr(project: str, number: str) -> PullRequest:
    """Fetch MR data from GitLab."""
    token = os.environ.get('GITLAB_TOKEN')
    if not token:
        print("Error: GITLAB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    import urllib.request
    import urllib.parse
    import urllib.error

    # URL-encode the project path
    encoded_project = urllib.parse.quote(project, safe='')
    base_url = f"https://gitlab.com/api/v4/projects/{encoded_project}/merge_requests/{number}"

    def api_request(endpoint: str) -> dict:
        url = f"{base_url}{endpoint}" if endpoint else base_url
        req = urllib.request.Request(url)
        req.add_header('PRIVATE-TOKEN', token)
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            print(f"GitLab API error: {e.code} {e.reason}", file=sys.stderr)
            sys.exit(1)

    # Fetch MR data
    mr_data = api_request('')

    # Fetch changes
    changes_data = api_request('/changes')

    # Parse files
    files = []
    for change in changes_data.get('changes', []):
        status = 'modified'
        if change.get('new_file'):
            status = 'added'
        elif change.get('deleted_file'):
            status = 'deleted'
        elif change.get('renamed_file'):
            status = 'renamed'

        # GitLab doesn't provide line counts in changes endpoint
        diff_lines = change.get('diff', '').split('\n')
        additions = len([l for l in diff_lines if l.startswith('+') and not l.startswith('+++')])
        deletions = len([l for l in diff_lines if l.startswith('-') and not l.startswith('---')])

        files.append(FileChange(
            path=change.get('new_path', change.get('old_path', '')),
            additions=additions,
            deletions=deletions,
            status=status
        ))

    # Build diff from changes
    diff_parts = []
    for change in changes_data.get('changes', []):
        diff_parts.append(f"diff --git a/{change.get('old_path')} b/{change.get('new_path')}")
        diff_parts.append(change.get('diff', ''))
    diff = '\n'.join(diff_parts)

    # Fetch commits
    commits_data = api_request('/commits')
    commits = []
    for c in commits_data:
        commits.append(Commit(
            sha=c.get('short_id', c.get('id', '')[:8]),
            message=c.get('title', ''),
            author=c.get('author_name', '')
        ))

    return PullRequest(
        platform='gitlab',
        number=int(number),
        title=mr_data.get('title', ''),
        description=mr_data.get('description', ''),
        author=mr_data.get('author', {}).get('username', ''),
        state=mr_data.get('state', 'opened'),
        base_branch=mr_data.get('target_branch', ''),
        head_branch=mr_data.get('source_branch', ''),
        files_changed=files,
        commits=commits,
        diff=diff
    )


def fetch_bitbucket_pr(workspace: str, repo: str, number: str) -> PullRequest:
    """Fetch PR data from Bitbucket."""
    username = os.environ.get('BITBUCKET_USERNAME')
    password = os.environ.get('BITBUCKET_APP_PASSWORD')

    if not username or not password:
        print("Error: BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD environment variables required", file=sys.stderr)
        sys.exit(1)

    import urllib.request
    import urllib.error
    import base64

    base_url = f"https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{number}"

    def api_request(endpoint: str = '') -> dict:
        url = f"{base_url}{endpoint}"
        req = urllib.request.Request(url)
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        req.add_header('Authorization', f'Basic {credentials}')
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"PR not found: {workspace}/{repo}/pull-requests/{number}", file=sys.stderr)
            else:
                print(f"Bitbucket API error: {e.code} {e.reason}", file=sys.stderr)
            sys.exit(1)

    def get_diff() -> str:
        url = f"{base_url}/diff"
        req = urllib.request.Request(url)
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        req.add_header('Authorization', f'Basic {credentials}')
        try:
            with urllib.request.urlopen(req) as response:
                return response.read().decode()
        except urllib.error.HTTPError:
            return ""

    # Fetch PR data
    pr_data = api_request()

    # Fetch diffstat for file changes
    diffstat = api_request('/diffstat')

    files = []
    for value in diffstat.get('values', []):
        old_path = value.get('old', {}).get('path', '')
        new_path = value.get('new', {}).get('path', '')
        status = value.get('status', 'modified')

        files.append(FileChange(
            path=new_path or old_path,
            additions=value.get('lines_added', 0),
            deletions=value.get('lines_removed', 0),
            status=status
        ))

    # Fetch commits
    commits_data = api_request('/commits')
    commits = []
    for c in commits_data.get('values', []):
        commits.append(Commit(
            sha=c.get('hash', '')[:8],
            message=c.get('message', '').split('\n')[0],
            author=c.get('author', {}).get('user', {}).get('display_name', '')
        ))

    # Fetch diff
    diff = get_diff()

    return PullRequest(
        platform='bitbucket',
        number=int(number),
        title=pr_data.get('title', ''),
        description=pr_data.get('description', ''),
        author=pr_data.get('author', {}).get('display_name', ''),
        state=pr_data.get('state', 'OPEN').lower(),
        base_branch=pr_data.get('destination', {}).get('branch', {}).get('name', ''),
        head_branch=pr_data.get('source', {}).get('branch', {}).get('name', ''),
        files_changed=files,
        commits=commits,
        diff=diff
    )


def main():
    parser = argparse.ArgumentParser(description='Fetch PR/MR data from code hosting platforms')
    parser.add_argument('url', help='Pull request URL')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--diff-only', action='store_true', help='Only output diff')

    args = parser.parse_args()

    # Detect platform
    info = detect_platform(args.url)
    if not info:
        print(f"Error: Could not detect platform from URL: {args.url}", file=sys.stderr)
        print("Supported platforms: GitHub, GitLab, Bitbucket", file=sys.stderr)
        sys.exit(1)

    platform = info['platform']

    # Fetch PR data
    if platform == 'github':
        pr = fetch_github_pr(info['owner'], info['repo'], info['number'])
    elif platform == 'gitlab':
        pr = fetch_gitlab_mr(info['project'], info['number'])
    elif platform == 'bitbucket':
        pr = fetch_bitbucket_pr(info['workspace'], info['repo'], info['number'])
    else:
        print(f"Unsupported platform: {platform}", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.diff_only:
        print(pr.diff)
    elif args.json:
        # Convert dataclasses to dict
        pr_dict = asdict(pr)
        print(json.dumps(pr_dict, indent=2))
    else:
        print(f"Platform: {pr.platform.upper()}")
        print(f"PR #{pr.number}: {pr.title}")
        print(f"Author: {pr.author}")
        print(f"State: {pr.state}")
        print(f"Branches: {pr.head_branch} → {pr.base_branch}")
        print(f"\nDescription:\n{pr.description[:500]}{'...' if len(pr.description) > 500 else ''}")
        print(f"\nFiles Changed ({len(pr.files_changed)}):")
        for f in pr.files_changed[:20]:  # Limit to first 20
            print(f"  {f.status:10} {f.path} (+{f.additions}/-{f.deletions})")
        if len(pr.files_changed) > 20:
            print(f"  ... and {len(pr.files_changed) - 20} more files")
        print(f"\nCommits ({len(pr.commits)}):")
        for c in pr.commits[:10]:  # Limit to first 10
            print(f"  {c.sha} {c.message[:60]}")
        if len(pr.commits) > 10:
            print(f"  ... and {len(pr.commits) - 10} more commits")


if __name__ == '__main__':
    main()
