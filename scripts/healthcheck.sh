#!/bin/bash
#
# Health check script for Chess application
# Pings the /stats endpoint to verify API + Database connectivity
#
# Usage: ./healthcheck.sh [BASE_URL]
#
# Exit codes:
#   0 - All checks passed
#   1 - Health check failed
#

set -euo pipefail

# Configuration
BASE_URL="${1:-http://localhost:8080}"
STATS_ENDPOINT="${BASE_URL}/stats"
TIMEOUT=10
RETRIES=3
RETRY_DELAY=2

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if curl is available
check_dependencies() {
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed."
        exit 1
    fi
}

# Test a known FEN position that should exist in a properly seeded database
# If database is empty, we use /minimax which doesn't require DB data
check_api_health() {
    local endpoint="$1"
    local retry_count=0
    local response
    local http_code

    log_info "Checking endpoint: ${endpoint}"

    while [ $retry_count -lt $RETRIES ]; do
        # Make request and capture both response body and HTTP status code
        response=$(curl -s -w "\n%{http_code}" \
            --connect-timeout "$TIMEOUT" \
            --max-time "$TIMEOUT" \
            "$endpoint" 2>&1) || true

        # Extract HTTP status code (last line)
        http_code=$(echo "$response" | tail -n1)
        # Extract response body (all but last line)
        body=$(echo "$response" | sed '$d')

        # Check for successful response (200-299) or expected 404 (position not in empty DB)
        if [[ "$http_code" =~ ^2[0-9][0-9]$ ]]; then
            log_info "✓ Endpoint returned HTTP ${http_code}"
            return 0
        elif [[ "$http_code" == "404" ]]; then
            # 404 is acceptable for /stats - means API is up but position not found
            log_warn "Endpoint returned HTTP 404 - API is up, position not in database"
            return 0
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $RETRIES ]; then
                log_warn "Request failed (HTTP ${http_code}), retrying in ${RETRY_DELAY}s... (${retry_count}/${RETRIES})"
                sleep "$RETRY_DELAY"
            fi
        fi
    done

    log_error "Health check failed after ${RETRIES} attempts (last HTTP code: ${http_code})"
    return 1
}

# Check minimax endpoint (doesn't require database data)
check_minimax_health() {
    local starting_fen="rnbqkbnr%2Fpppppppp%2F8%2F8%2F8%2F8%2FPPPPPPPP%2FRNBQKBNR%20w%20KQkq%20-"
    local endpoint="${BASE_URL}/minimax?fen=${starting_fen}&depth=1"

    log_info "Checking minimax endpoint (compute-only, no DB required)..."

    local response
    local http_code

    response=$(curl -s -w "\n%{http_code}" \
        --connect-timeout "$TIMEOUT" \
        --max-time 30 \
        "$endpoint" 2>&1) || true

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [[ "$http_code" =~ ^2[0-9][0-9]$ ]]; then
        # Verify response contains expected fields
        if echo "$body" | grep -q '"best_move"'; then
            log_info "✓ Minimax endpoint healthy - returned valid move data"
            return 0
        else
            log_error "Minimax endpoint returned unexpected response format"
            return 1
        fi
    else
        log_error "Minimax health check failed (HTTP ${http_code})"
        return 1
    fi
}

# Check database connectivity via /stats with a test FEN
check_database_health() {
    # Use starting position FEN (may or may not exist in DB)
    local test_fen="rnbqkbnr%2Fpppppppp%2F8%2F8%2F8%2F8%2FPPPPPPPP%2FRNBQKBNR%20w%20KQkq%20-"
    local endpoint="${STATS_ENDPOINT}?fen=${test_fen}"

    log_info "Checking database connectivity via /stats endpoint..."
    check_api_health "$endpoint"
}

# Main health check routine
main() {
    log_info "Starting health check for Chess API at ${BASE_URL}"
    log_info "================================================"

    check_dependencies

    local all_passed=true

    # Check 1: API basic connectivity (minimax - doesn't need DB data)
    if ! check_minimax_health; then
        log_error "API connectivity check FAILED"
        all_passed=false
    fi

    echo ""

    # Check 2: Database connectivity
    if ! check_database_health; then
        log_error "Database connectivity check FAILED"
        all_passed=false
    fi

    echo ""
    log_info "================================================"

    if [ "$all_passed" = true ]; then
        log_info "✓ All health checks PASSED"
        exit 0
    else
        log_error "✗ One or more health checks FAILED"
        exit 1
    fi
}

# Run main function
main
