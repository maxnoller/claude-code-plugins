#!/usr/bin/env bash

# Moon Configuration Verification Script
# Validates moon configuration files for syntax and common issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
CHECKED=0

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((ERRORS++)) || true
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARNINGS++)) || true
}

log_ok() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Validate YAML syntax
validate_yaml_syntax() {
    local file=$1
    ((CHECKED++)) || true

    if command_exists python3; then
        if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            log_ok "YAML syntax valid: $file"
            return 0
        else
            log_error "Invalid YAML syntax: $file"
            python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>&1 | head -5
            return 1
        fi
    elif command_exists yq; then
        if yq eval '.' "$file" >/dev/null 2>&1; then
            log_ok "YAML syntax valid: $file"
            return 0
        else
            log_error "Invalid YAML syntax: $file"
            return 1
        fi
    else
        log_warn "No YAML validator available (install python3 with pyyaml or yq)"
        return 0
    fi
}

# Check workspace.yml for common issues
check_workspace_config() {
    local file=$1

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    log_info "Checking workspace configuration..."

    # Check projects field exists
    if ! grep -q "^projects:" "$file" 2>/dev/null; then
        log_error "workspace.yml missing 'projects' field"
    fi

    # Check vcs configuration
    if grep -q "^vcs:" "$file" 2>/dev/null; then
        if ! grep -q "defaultBranch:" "$file" 2>/dev/null; then
            log_warn "workspace.yml: VCS section missing 'defaultBranch'"
        fi
    fi
}

# Check toolchain.yml for common issues
check_toolchain_config() {
    local file=$1

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    log_info "Checking toolchain configuration..."

    # Check for version fields
    if grep -q "node:" "$file" 2>/dev/null; then
        if ! grep -q "version:" "$file" 2>/dev/null; then
            log_warn "toolchain.yml: Node section missing 'version'"
        fi
    fi
}

# Check moon.yml project config
check_project_config() {
    local file=$1

    log_info "Checking project: $file"

    # Check for tasks without inputs
    if grep -q "^tasks:" "$file" 2>/dev/null; then
        # Simple heuristic: tasks with command but no inputs
        local in_task=false
        local has_inputs=false
        local task_name=""

        while IFS= read -r line; do
            if [[ "$line" =~ ^[[:space:]]{2}[a-zA-Z] && ! "$line" =~ ^[[:space:]]{4} ]]; then
                # New task definition
                if [[ "$in_task" == true && "$has_inputs" == false && -n "$task_name" ]]; then
                    log_warn "$file: Task '$task_name' has no inputs defined"
                fi
                task_name=$(echo "$line" | sed 's/://g' | xargs)
                in_task=true
                has_inputs=false
            elif [[ "$line" =~ inputs: ]]; then
                has_inputs=true
            fi
        done < <(sed -n '/^tasks:/,/^[a-z]/p' "$file" | head -100)
    fi
}

# Check tasks.yml inherited config
check_tasks_config() {
    local file=$1

    if [[ ! -f "$file" ]]; then
        return 0
    fi

    log_info "Checking inherited tasks: $file"

    # Check for fileGroups
    if ! grep -q "^fileGroups:" "$file" 2>/dev/null; then
        log_warn "tasks.yml: Consider defining fileGroups for consistent inputs"
    fi
}

# Run moon check if available
run_moon_check() {
    if command_exists moon; then
        log_info "Running 'moon check'..."
        if moon check 2>&1; then
            log_ok "moon check passed"
        else
            log_error "moon check failed"
        fi
    else
        log_info "moon CLI not installed, skipping 'moon check'"
    fi
}

# Main function
main() {
    local target_dir="${1:-.}"

    echo "============================================"
    echo "Moon Configuration Verification"
    echo "Target: $target_dir"
    echo "============================================"
    echo ""

    cd "$target_dir"

    # Check .moon directory exists
    if [[ ! -d ".moon" ]]; then
        log_error "No .moon directory found. Is this a moon workspace?"
        exit 1
    fi

    # Validate workspace.yml
    if [[ -f ".moon/workspace.yml" ]]; then
        validate_yaml_syntax ".moon/workspace.yml"
        check_workspace_config ".moon/workspace.yml"
    else
        log_error ".moon/workspace.yml not found"
    fi

    # Validate toolchain.yml
    if [[ -f ".moon/toolchain.yml" ]]; then
        validate_yaml_syntax ".moon/toolchain.yml"
        check_toolchain_config ".moon/toolchain.yml"
    fi

    # Validate tasks.yml
    if [[ -f ".moon/tasks.yml" ]]; then
        validate_yaml_syntax ".moon/tasks.yml"
        check_tasks_config ".moon/tasks.yml"
    fi

    # Validate language-specific tasks
    for file in .moon/tasks/*.yml; do
        if [[ -f "$file" ]]; then
            validate_yaml_syntax "$file"
        fi
    done

    # Find and validate all moon.yml files
    while IFS= read -r -d '' file; do
        validate_yaml_syntax "$file"
        check_project_config "$file"
    done < <(find . -name "moon.yml" -not -path "./.moon/*" -print0 2>/dev/null)

    # Validate .prototools if exists
    if [[ -f ".prototools" ]]; then
        log_info "Found .prototools"
        ((CHECKED++)) || true
        log_ok ".prototools exists"
    fi

    # Run moon check
    echo ""
    run_moon_check

    # Summary
    echo ""
    echo "============================================"
    echo "Summary"
    echo "============================================"
    echo "Files checked: $CHECKED"
    echo -e "Errors: ${RED}$ERRORS${NC}"
    echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
    echo ""

    if [[ $ERRORS -gt 0 ]]; then
        echo -e "${RED}Verification FAILED${NC}"
        exit 1
    elif [[ $WARNINGS -gt 0 ]]; then
        echo -e "${YELLOW}Verification PASSED with warnings${NC}"
        exit 0
    else
        echo -e "${GREEN}Verification PASSED${NC}"
        exit 0
    fi
}

# Run main
main "$@"
