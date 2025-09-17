#!/bin/bash

# Configuration Validation Script for AI Trading Assistant

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

CONFIG_FILE="etrade_python_client/config.ini"

print_header() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}\n"
}

print_step() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}🎉 $1${NC}"
}

validate_file_exists() {
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        echo "Please run ./setup.sh to create the configuration file."
        exit 1
    fi
    print_step "Configuration file exists"
}

validate_config_structure() {
    print_info "Validating configuration file structure..."
    
    local required_sections=("DEFAULT" "AI_SERVICES" "WEB_APP" "DATABASE" "NOTIFICATIONS" "CELERY")
    local errors=0
    
    for section in "${required_sections[@]}"; do
        if grep -q "\\[$section\\]" "$CONFIG_FILE"; then
            print_step "Section [$section] found"
        else
            print_error "Missing section: [$section]"
            errors=$((errors + 1))
        fi
    done
    
    return $errors
}

validate_etrade_config() {
    print_info "Validating E*TRADE configuration..."
    
    local errors=0
    
    # Check if consumer key is set
    if grep -q "CONSUMER_KEY = [a-zA-Z0-9]" "$CONFIG_FILE"; then
        print_step "E*TRADE Consumer Key is configured"
    else
        print_warning "E*TRADE Consumer Key appears to be using default/empty value"
    fi
    
    # Check if consumer secret is set
    if grep -q "CONSUMER_SECRET = [a-zA-Z0-9]" "$CONFIG_FILE"; then
        print_step "E*TRADE Consumer Secret is configured"
    else
        print_warning "E*TRADE Consumer Secret appears to be using default/empty value"
    fi
    
    # Check base URLs
    if grep -q "SANDBOX_BASE_URL = " "$CONFIG_FILE" && grep -q "PROD_BASE_URL = " "$CONFIG_FILE"; then
        print_step "E*TRADE base URLs configured (sandbox and production)"
        
        sandbox_url=$(grep "SANDBOX_BASE_URL = " "$CONFIG_FILE" | cut -d'=' -f2 | tr -d ' ')
        prod_url=$(grep "PROD_BASE_URL = " "$CONFIG_FILE" | cut -d'=' -f2 | tr -d ' ')
        
        if [[ $sandbox_url == *"apisb.etrade.com"* ]]; then
            print_info "Sandbox URL correctly configured"
        else
            print_warning "Sandbox URL may be incorrect: $sandbox_url"
        fi
        
        if [[ $prod_url == *"api.etrade.com"* ]]; then
            print_info "Production URL correctly configured"
        else
            print_warning "Production URL may be incorrect: $prod_url"
        fi
    else
        print_error "E*TRADE base URLs not found"
        errors=$((errors + 1))
    fi
    
    return $errors
}

validate_ai_services() {
    print_info "Validating AI services configuration..."
    
    local errors=0
    
    # Check Gemini API key
    gemini_key=$(grep "GEMINI_API_KEY = " "$CONFIG_FILE" | cut -d'=' -f2 | tr -d ' ')
    if [ -n "$gemini_key" ] && [ "$gemini_key" != "your_actual_gemini_api_key_here" ]; then
        print_step "Google Gemini API key is configured"
    else
        print_error "Google Gemini API key is not configured or using default value"
        print_info "Get your API key from: https://makersuite.google.com/app/apikey"
        errors=$((errors + 1))
    fi
    
    return $errors
}

validate_notifications() {
    print_info "Validating notification configuration..."
    
    local has_email=false
    local has_slack=false
    
    # Check email configuration
    if grep -q "smtp_username = [a-zA-Z0-9@]" "$CONFIG_FILE" && \
       grep -q "smtp_password = [a-zA-Z0-9]" "$CONFIG_FILE"; then
        print_step "Email notifications configured"
        has_email=true
    fi
    
    # Check Slack configuration
    if grep -q "slack_bot_token = xoxb-" "$CONFIG_FILE"; then
        print_step "Slack notifications configured"
        has_slack=true
    fi
    
    if [ "$has_email" = false ] && [ "$has_slack" = false ]; then
        print_warning "No notification services configured (optional)"
        print_info "You can configure email/Slack notifications later"
    fi
    
    return 0
}

validate_web_app() {
    print_info "Validating web application configuration..."
    
    local errors=0
    
    # Check host configuration
    host=$(grep "HOST = " "$CONFIG_FILE" | cut -d'=' -f2 | tr -d ' ')
    if [ -n "$host" ]; then
        print_step "Web app host configured: $host"
    else
        print_error "Web app host not configured"
        errors=$((errors + 1))
    fi
    
    # Check port configuration
    port=$(grep "PORT = " "$CONFIG_FILE" | cut -d'=' -f2 | tr -d ' ')
    if [[ $port =~ ^[0-9]+$ ]] && [ "$port" -gt 1000 ] && [ "$port" -lt 65536 ]; then
        print_step "Web app port configured: $port"
    else
        print_error "Invalid web app port: $port"
        errors=$((errors + 1))
    fi
    
    return $errors
}

validate_database() {
    print_info "Validating database configuration..."
    
    local errors=0
    
    # Check database URL
    db_url=$(grep "DATABASE_URL = " "$CONFIG_FILE" | cut -d'=' -f2 | tr -d ' ')
    if [[ $db_url == sqlite* ]]; then
        print_step "SQLite database configured"
        
        # Check if data directory exists
        if [ -d "data" ]; then
            print_step "Data directory exists"
        else
            print_info "Data directory will be created when needed"
        fi
    else
        print_error "Invalid database URL: $db_url"
        errors=$((errors + 1))
    fi
    
    return $errors
}

validate_celery() {
    print_info "Validating Celery configuration..."
    
    local errors=0
    
    # Check broker URL
    broker_url=$(grep "BROKER_URL = " "$CONFIG_FILE" | cut -d'=' -f2 | tr -d ' ')
    if [[ $broker_url == redis* ]]; then
        print_step "Redis broker configured for Celery"
    else
        print_error "Invalid Celery broker URL: $broker_url"
        errors=$((errors + 1))
    fi
    
    return $errors
}

test_api_connectivity() {
    print_info "Testing API connectivity (optional)..."
    
    # Test if we can reach external APIs
    if command -v curl >/dev/null 2>&1; then
        # Test Yahoo Finance API
        if curl -s --max-time 5 "https://query1.finance.yahoo.com/v8/finance/chart/AAPL" > /dev/null; then
            print_step "Yahoo Finance API accessible"
        else
            print_warning "Cannot reach Yahoo Finance API (may be network/firewall issue)"
        fi
        
        # Test Google AI API (basic connectivity)
        if curl -s --max-time 5 "https://generativelanguage.googleapis.com" > /dev/null; then
            print_step "Google AI API endpoint accessible"
        else
            print_warning "Cannot reach Google AI API (may be network/firewall issue)"
        fi
    else
        print_info "curl not available, skipping connectivity tests"
    fi
}

check_docker_environment() {
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        print_info "Docker environment detected"
        
        # Check if docker-compose files exist
        if [ -f "docker-compose.yml" ]; then
            print_step "Docker Compose configuration found"
        else
            print_warning "Docker Compose configuration not found"
        fi
        
        return 0
    else
        print_info "Docker not available or not running"
        return 1
    fi
}

check_manual_environment() {
    print_info "Checking manual setup environment..."
    
    local warnings=0
    
    # Check Python
    if command -v python3 >/dev/null 2>&1; then
        python_version=$(python3 --version | cut -d' ' -f2)
        print_step "Python 3 available: $python_version"
    else
        print_warning "Python 3 not found"
        warnings=$((warnings + 1))
    fi
    
    # Check Node.js
    if command -v node >/dev/null 2>&1; then
        node_version=$(node --version)
        print_step "Node.js available: $node_version"
    else
        print_warning "Node.js not found"
        warnings=$((warnings + 1))
    fi
    
    # Check Redis
    if command -v redis-server >/dev/null 2>&1; then
        print_step "Redis server available"
    else
        print_warning "Redis server not found"
        warnings=$((warnings + 1))
    fi
    
    # Check virtual environment
    if [ -d "venv" ]; then
        print_step "Python virtual environment exists"
    else
        print_info "Python virtual environment not created yet"
    fi
    
    # Check frontend dependencies
    if [ -d "frontend/node_modules" ]; then
        print_step "Frontend dependencies installed"
    else
        print_info "Frontend dependencies not installed yet"
    fi
    
    return $warnings
}

generate_summary() {
    local total_errors=$1
    local total_warnings=$2
    
    print_header "Validation Summary"
    
    if [ $total_errors -eq 0 ]; then
        print_success "Configuration validation passed!"
        echo -e "${GREEN}✓ No critical errors found${NC}"
    else
        print_error "Configuration validation failed with $total_errors critical errors"
        echo -e "${RED}Please fix the errors above before starting the application${NC}"
    fi
    
    if [ $total_warnings -gt 0 ]; then
        echo -e "${YELLOW}⚠ $total_warnings warnings found (non-critical)${NC}"
    fi
    
    echo
    print_info "Next steps:"
    if [ $total_errors -eq 0 ]; then
        echo -e "  1. ${GREEN}Start the application with: ./scripts/docker-dev.sh${NC}"
        echo -e "  2. ${GREEN}Or start manually following README instructions${NC}"
        echo -e "  3. ${GREEN}Open http://localhost:3000 in your browser${NC}"
    else
        echo -e "  1. ${RED}Fix the configuration errors listed above${NC}"
        echo -e "  2. ${RED}Run this validation script again${NC}"
        echo -e "  3. ${RED}Or re-run the setup script: ./setup.sh${NC}"
    fi
}

main() {
    print_header "AI Trading Assistant - Configuration Validation"
    
    local total_errors=0
    local total_warnings=0
    
    # Basic file validation
    validate_file_exists
    
    # Configuration structure validation
    validate_config_structure
    total_errors=$((total_errors + $?))
    
    # Individual section validations
    validate_etrade_config
    total_warnings=$((total_warnings + $?))
    
    validate_ai_services
    total_errors=$((total_errors + $?))
    
    validate_notifications
    # Notifications are optional, so don't count as errors
    
    validate_web_app
    total_errors=$((total_errors + $?))
    
    validate_database
    total_errors=$((total_errors + $?))
    
    validate_celery
    total_errors=$((total_errors + $?))
    
    # Environment checks
    if check_docker_environment; then
        print_info "Docker environment validation complete"
    else
        check_manual_environment
        total_warnings=$((total_warnings + $?))
    fi
    
    # Optional connectivity tests
    test_api_connectivity
    
    # Generate summary
    generate_summary $total_errors $total_warnings
    
    # Exit with appropriate code
    if [ $total_errors -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

main "$@"