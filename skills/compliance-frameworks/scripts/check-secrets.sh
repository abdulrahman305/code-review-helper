#!/bin/bash
# Secret detection script for compliance review
# Scans for hardcoded secrets, API keys, and credentials

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Patterns to detect secrets
declare -A PATTERNS=(
    # AWS
    ["AWS_ACCESS_KEY"]='AKIA[0-9A-Z]{16}'
    ["AWS_SECRET_KEY"]='(?i)aws[_-]?secret[_-]?access[_-]?key.*[=:]\s*["\x27][A-Za-z0-9/+=]{40}["\x27]'

    # GitHub
    ["GITHUB_TOKEN"]='ghp_[a-zA-Z0-9]{36}'
    ["GITHUB_PAT"]='github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}'

    # Generic API Keys
    ["API_KEY"]='(?i)(api[_-]?key|apikey)["\x27]?\s*[=:]\s*["\x27][a-zA-Z0-9]{20,}["\x27]'
    ["SECRET_KEY"]='(?i)(secret[_-]?key|secretkey)["\x27]?\s*[=:]\s*["\x27][a-zA-Z0-9]{20,}["\x27]'

    # Passwords
    ["PASSWORD"]='(?i)(password|passwd|pwd)["\x27]?\s*[=:]\s*["\x27][^"\x27]{6,}["\x27]'

    # Private Keys
    ["PRIVATE_KEY"]='-----BEGIN\s+(RSA\s+|EC\s+|DSA\s+|OPENSSH\s+)?PRIVATE\s+KEY-----'

    # Database URLs with credentials
    ["DATABASE_URL"]='(?i)(mysql|postgres|mongodb|redis)://[^:]+:[^@]+@'

    # JWT Tokens
    ["JWT_TOKEN"]='eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'

    # Slack
    ["SLACK_TOKEN"]='xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*'

    # Google
    ["GOOGLE_API"]='AIza[0-9A-Za-z_-]{35}'
    ["GCP_SERVICE_ACCOUNT"]='"type"\s*:\s*"service_account"'

    # Stripe
    ["STRIPE_KEY"]='(?:sk|pk)_(live|test)_[0-9a-zA-Z]{24,}'

    # SendGrid
    ["SENDGRID_KEY"]='SG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}'

    # Twilio
    ["TWILIO_KEY"]='SK[0-9a-fA-F]{32}'

    # Generic High-Entropy Strings (potential secrets)
    ["HIGH_ENTROPY"]='(?i)(secret|token|key|password|credential)["\x27]?\s*[=:]\s*["\x27][A-Za-z0-9+/=]{32,}["\x27]'
)

# Files to exclude
EXCLUDE_PATTERNS=(
    "*.min.js"
    "*.min.css"
    "package-lock.json"
    "yarn.lock"
    "*.svg"
    "*.png"
    "*.jpg"
    "*.gif"
    "*.ico"
    "*.woff*"
    "*.ttf"
    "*.eot"
)

# Directories to exclude
EXCLUDE_DIRS=(
    "node_modules"
    ".git"
    "__pycache__"
    "venv"
    ".venv"
    "vendor"
    "dist"
    "build"
    ".next"
    "coverage"
)

usage() {
    echo "Usage: $0 <path> [--json]"
    echo ""
    echo "Scan for hardcoded secrets in source code"
    echo ""
    echo "Options:"
    echo "  --json    Output results in JSON format"
    echo "  --help    Show this help message"
    exit 1
}

# Check arguments
if [ $# -lt 1 ] || [ "$1" == "--help" ]; then
    usage
fi

TARGET_PATH="$1"
JSON_OUTPUT=false

if [ "$2" == "--json" ]; then
    JSON_OUTPUT=true
fi

if [ ! -e "$TARGET_PATH" ]; then
    echo "Error: Path not found: $TARGET_PATH"
    exit 1
fi

# Build exclude arguments for grep
EXCLUDE_ARGS=""
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$pattern"
done

for dir in "${EXCLUDE_DIRS[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude-dir=$dir"
done

# Track findings
declare -a FINDINGS
CRITICAL_COUNT=0
HIGH_COUNT=0

scan_pattern() {
    local name="$1"
    local pattern="$2"
    local results

    if [ -f "$TARGET_PATH" ]; then
        results=$(grep -Pn "$pattern" "$TARGET_PATH" 2>/dev/null || true)
    else
        results=$(grep -Prn $EXCLUDE_ARGS "$pattern" "$TARGET_PATH" 2>/dev/null || true)
    fi

    if [ -n "$results" ]; then
        while IFS= read -r line; do
            if [ -n "$line" ]; then
                FINDINGS+=("$name|$line")

                # Count severity
                case "$name" in
                    "PRIVATE_KEY"|"AWS_ACCESS_KEY"|"AWS_SECRET_KEY"|"DATABASE_URL")
                        ((CRITICAL_COUNT++))
                        ;;
                    *)
                        ((HIGH_COUNT++))
                        ;;
                esac
            fi
        done <<< "$results"
    fi
}

# Scan for each pattern
echo "Scanning for secrets..." >&2
for name in "${!PATTERNS[@]}"; do
    scan_pattern "$name" "${PATTERNS[$name]}"
done

# Output results
if $JSON_OUTPUT; then
    echo "["
    first=true
    for finding in "${FINDINGS[@]}"; do
        IFS='|' read -r type location <<< "$finding"
        file=$(echo "$location" | cut -d: -f1)
        line=$(echo "$location" | cut -d: -f2)
        code=$(echo "$location" | cut -d: -f3-)

        # Determine severity
        severity="high"
        case "$type" in
            "PRIVATE_KEY"|"AWS_ACCESS_KEY"|"AWS_SECRET_KEY"|"DATABASE_URL")
                severity="critical"
                ;;
        esac

        if ! $first; then
            echo ","
        fi
        first=false

        # Mask the actual secret in output
        masked_code=$(echo "$code" | sed -E 's/(["\x27])[A-Za-z0-9+/=_-]{8,}(["\x27])/\1***REDACTED***\2/g')

        cat << EOF
  {
    "type": "$type",
    "severity": "$severity",
    "file": "$file",
    "line": $line,
    "code": "$masked_code"
  }
EOF
    done
    echo ""
    echo "]"
else
    if [ ${#FINDINGS[@]} -eq 0 ]; then
        echo -e "${GREEN}No secrets detected.${NC}"
        exit 0
    fi

    echo ""
    echo -e "${RED}=== SECRET DETECTION RESULTS ===${NC}"
    echo ""
    echo "Found ${#FINDINGS[@]} potential secret(s)"
    echo ""

    current_type=""
    for finding in "${FINDINGS[@]}"; do
        IFS='|' read -r type location <<< "$finding"

        if [ "$type" != "$current_type" ]; then
            current_type="$type"
            echo -e "\n${YELLOW}[$type]${NC}"
        fi

        file=$(echo "$location" | cut -d: -f1)
        line=$(echo "$location" | cut -d: -f2)
        code=$(echo "$location" | cut -d: -f3-)

        # Mask secrets in display
        masked_code=$(echo "$code" | sed -E 's/(["\x27])[A-Za-z0-9+/=_-]{8,}(["\x27])/\1***REDACTED***\2/g')

        echo "  File: $file:$line"
        echo "  Code: $masked_code"
        echo ""
    done

    echo "================================"
    echo ""
    echo "Summary:"
    echo -e "  ${RED}Critical: $CRITICAL_COUNT${NC}"
    echo -e "  ${YELLOW}High: $HIGH_COUNT${NC}"
    echo ""
    echo "Recommendations:"
    echo "  1. Remove secrets from source code"
    echo "  2. Rotate any exposed credentials immediately"
    echo "  3. Use environment variables or a secrets manager"
    echo "  4. Add patterns to .gitignore and pre-commit hooks"
fi

# Exit with error if secrets found
if [ ${#FINDINGS[@]} -gt 0 ]; then
    exit 1
fi
exit 0
