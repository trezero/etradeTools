#!/bin/bash

# AI Trading Assistant - Comprehensive Setup Script
# This script guides you through the complete setup process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration variables
SETUP_MODE=""
USE_DOCKER=true
CONFIG_FILE="etrade_python_client/config.ini"
CONFIG_TEMPLATE="etrade_python_client/config.ini.template"

# Function to print colored output
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

# Function to prompt user input in a field-like format
prompt_input_field() {
    local prompt="$1"
    local secret="$2"
    local response=""

    echo -e "${PURPLE}$prompt:${NC}"
    echo -e "${CYAN}┌───────────────────────────────────────────────────┐${NC}"
    echo -n -e "${CYAN}│ ${NC}"

    if [ "$secret" = "true" ]; then
        read -s response
    else
        read response
    fi

    echo -e "
${CYAN}└───────────────────────────────────────────────────┘${NC}"

    echo "$response"
}

# Function to prompt user input
prompt_input() {
    local prompt="$1"
    local default="$2"
    local secret="$3"
    local response=""
    
    if [ "$secret" = "true" ]; then
        echo -n -e "${PURPLE}$prompt${NC}"
        if [ -n "$default" ]; then
            echo -n " (default: ***): "
        else
            echo -n " (required): "
        fi
        read -s response
        echo
    else
        echo -n -e "${PURPLE}$prompt${NC}"
        if [ -n "$default" ]; then
            echo -n " (default: $default): "
        else
            echo -n " (required): "
        fi
        read response
    fi
    
    if [ -z "$response" ] && [ -n "$default" ]; then
        response="$default"
    fi
    
    echo "$response"
}

# Function to validate input
validate_required() {
    local value="$1"
    local name="$2"
    
    if [ -z "$value" ]; then
        print_error "$name is required!"
        return 1
    fi
    return 0
}

# Function to validate email
validate_email() {
    local email="$1"
    if [[ $email =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker installation
check_docker() {
    print_info "Checking Docker installation..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed."
        echo -e "${YELLOW}Please install Docker from: https://docs.docker.com/get-docker/${NC}"
        echo -e "${YELLOW}After installation, run this script again.${NC}"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed."
        echo -e "${YELLOW}Please install Docker Compose from: https://docs.docker.com/compose/install/${NC}"
        echo -e "${YELLOW}After installation, run this script again.${NC}"
        exit 1
    fi
    
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running."
        echo -e "${YELLOW}Please start Docker and run this script again.${NC}"
        exit 1
    fi
    
    print_step "Docker is installed and running"
}

# Function to check manual setup requirements
check_manual_requirements() {
    print_info "Checking manual setup requirements..."
    
    local missing_deps=()
    
    # Check Python
    if ! command_exists python3; then
        missing_deps+=("Python 3.10+")
    else
        python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
            missing_deps+=("Python 3.10+ (current: $python_version)")
        fi
    fi
    
    # Check Node.js
    if ! command_exists node; then
        missing_deps+=("Node.js 18+")
    else
        node_version=$(node --version | sed 's/v//')
        node_major=$(echo $node_version | cut -d'.' -f1)
        if [ "$node_major" -lt 18 ]; then
            missing_deps+=("Node.js 18+ (current: $node_version)")
        fi
    fi
    
    # Check npm
    if ! command_exists npm; then
        missing_deps+=("npm")
    fi
    
    # Check Redis (optional warning)
    if ! command_exists redis-server; then
        print_warning "Redis server not found. You'll need to install Redis separately."
        print_info "Install Redis: https://redis.io/download"
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies:"
        for dep in "${missing_deps[@]}"; do
            echo -e "  ${RED}- $dep${NC}"
        done
        echo
        echo -e "${YELLOW}Please install the missing dependencies and run this script again.${NC}"
        exit 1
    fi
    
    print_step "All manual setup requirements are met"
}

# Function to create directories
create_directories() {
    print_info "Creating necessary directories..."
    
    mkdir -p data logs scripts
    chmod 755 scripts
    
    print_step "Directories created"
}

# Function to copy configuration template
copy_config_template() {
    print_info "Setting up configuration file..."
    
    if [ ! -f "$CONFIG_TEMPLATE" ]; then
        print_error "Configuration template not found: $CONFIG_TEMPLATE"
        print_info "Please ensure you're running this script from the project root directory."
        exit 1
    fi
    
    if [ -f "$CONFIG_FILE" ]; then
        echo -e "${YELLOW}Configuration file already exists.${NC}"
        backup_file="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}Creating backup: $backup_file${NC}"
        cp "$CONFIG_FILE" "$backup_file"
    fi
    
    cp "$CONFIG_TEMPLATE" "$CONFIG_FILE"
    print_step "Configuration file created"
}

# Function to configure E*TRADE settings
configure_etrade() {
    print_header "E*TRADE API Configuration"
    
    echo -e "${CYAN}E*TRADE provides sandbox credentials for testing.${NC}"
    echo -e "${CYAN}For production trading, you'll need your own API credentials.${NC}"
    echo
    
    # Ask if user wants to use production credentials
    echo -n -e "${PURPLE}Do you want to configure production E*TRADE credentials? (y/N): ${NC}"
    read use_production
    
    if [[ $use_production =~ ^[Yy]$ ]]; then
        print_info "Configure your production E*TRADE API credentials:"
        print_info "Get your credentials from: https://developer.etrade.com/getting-started"
        echo
        
        etrade_key=$(prompt_input "E*TRADE Consumer Key" "")
        validate_required "$etrade_key" "E*TRADE Consumer Key" || return 1
        
        etrade_secret=$(prompt_input "E*TRADE Consumer Secret" "" "true")
        validate_required "$etrade_secret" "E*TRADE Consumer Secret" || return 1
        
        # Update config file using safe configuration updater
        python3 scripts/update-config.py "$CONFIG_FILE" --section "DEFAULT" --key "CONSUMER_KEY" --value "$etrade_key"
        python3 scripts/update-config.py "$CONFIG_FILE" --section "DEFAULT" --key "CONSUMER_SECRET" --value "$etrade_secret"
        python3 scripts/update-config.py "$CONFIG_FILE" --section "DEFAULT" --key "PROD_BASE_URL" --value "https://api.etrade.com"
        
        print_warning "You are now configured for PRODUCTION trading with real money!"
        print_warning "Please test thoroughly in sandbox mode first."
    else
        print_info "Using sandbox credentials for testing (no real money involved)"
    fi
    
    print_step "E*TRADE configuration completed"
}

# Function to configure AI services
configure_ai_services() {
    print_header "AI Services Configuration"
    
    echo -e "${CYAN}The AI Trading Assistant uses Google Gemini for market analysis.${NC}"
    echo -e "${CYAN}Get your free API key from: https://makersuite.google.com/app/apikey${NC}"
    echo
    
    echo -e "${PURPLE}Gemini API Key:${NC}"
    gemini_key=$(prompt_input_field "" "false")
    validate_required "$gemini_key" "Google Gemini API Key" || return 1
    
    # Update config file using safe configuration updater
    python3 scripts/update-config.py "$CONFIG_FILE" --section "AI_SERVICES" --key "GEMINI_API_KEY" --value "$gemini_key"
    
    print_step "AI services configuration completed"
}

# Function to configure notifications
configure_notifications() {
    print_header "Notification Services Configuration (Optional)"
    
    echo -e "${CYAN}Configure email and Slack notifications for trading alerts.${NC}"
    echo -e "${CYAN}You can skip this and configure later.${NC}"
    echo
    
    # Email configuration
    echo -n -e "${PURPLE}Do you want to configure email notifications? (y/N): ${NC}"
    read configure_email
    
    if [[ $configure_email =~ ^[Yy]$ ]]; then
        print_info "Email Notification Setup:"
        print_info "For Gmail, use an App Password: https://support.google.com/accounts/answer/185833"
        echo
        
        while true; do
            smtp_username=$(prompt_input "SMTP Username (email address)" "")
            if [ -n "$smtp_username" ]; then
                if validate_email "$smtp_username"; then
                    break
                else
                    print_error "Please enter a valid email address"
                fi
            else
                break
            fi
        done
        
        if [ -n "$smtp_username" ]; then
            smtp_password=$(prompt_input "SMTP Password/App Password" "" "true")
            smtp_host=$(prompt_input "SMTP Host" "smtp.gmail.com")
            smtp_port=$(prompt_input "SMTP Port" "587")
            
            # Update config file using safe configuration updater
            python3 scripts/update-config.py "$CONFIG_FILE" --section "NOTIFICATIONS" --key "smtp_username" --value "$smtp_username"
            python3 scripts/update-config.py "$CONFIG_FILE" --section "NOTIFICATIONS" --key "smtp_password" --value "$smtp_password"
            python3 scripts/update-config.py "$CONFIG_FILE" --section "NOTIFICATIONS" --key "smtp_host" --value "$smtp_host"
            python3 scripts/update-config.py "$CONFIG_FILE" --section "NOTIFICATIONS" --key "smtp_port" --value "$smtp_port"
            
            print_step "Email notifications configured"
        fi
    fi
    
    # Slack configuration
    echo -n -e "${PURPLE}Do you want to configure Slack notifications? (y/N): ${NC}"
    read configure_slack
    
    if [[ $configure_slack =~ ^[Yy]$ ]]; then
        print_info "Slack Notification Setup:"
        print_info "Create a Slack app and bot: https://api.slack.com/apps"
        echo
        
        slack_token=$(prompt_input "Slack Bot Token (xoxb-...)" "" "true")
        if [ -n "$slack_token" ]; then
            slack_channel=$(prompt_input "Slack Channel" "#trading-alerts")
            
            # Update config file using safe configuration updater
            python3 scripts/update-config.py "$CONFIG_FILE" --section "NOTIFICATIONS" --key "slack_bot_token" --value "$slack_token"
            python3 scripts/update-config.py "$CONFIG_FILE" --section "NOTIFICATIONS" --key "slack_channel" --value "$slack_channel"
            
            print_step "Slack notifications configured"
        fi
    fi
    
    if [[ ! $configure_email =~ ^[Yy]$ ]] && [[ ! $configure_slack =~ ^[Yy]$ ]]; then
        print_info "Notification services skipped (can be configured later)"
    fi
}

# Function to configure advanced settings
configure_advanced() {
    print_header "Advanced Configuration (Optional)"
    
    echo -e "${CYAN}Configure advanced settings for web server and database.${NC}"
    echo
    
    echo -n -e "${PURPLE}Do you want to configure advanced settings? (y/N): ${NC}"
    read configure_advanced_settings
    
    if [[ $configure_advanced_settings =~ ^[Yy]$ ]]; then
        web_host=$(prompt_input "Web Server Host" "0.0.0.0")
        web_port=$(prompt_input "Web Server Port" "8000")
        debug_mode=$(prompt_input "Enable Debug Mode" "false")
        
        # Update config file using safe configuration updater
        python3 scripts/update-config.py "$CONFIG_FILE" --section "WEB_APP" --key "HOST" --value "$web_host"
        python3 scripts/update-config.py "$CONFIG_FILE" --section "WEB_APP" --key "PORT" --value "$web_port"
        python3 scripts/update-config.py "$CONFIG_FILE" --section "WEB_APP" --key "DEBUG" --value "$debug_mode"
        
        print_step "Advanced settings configured"
    else
        print_info "Using default advanced settings"
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    print_info "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements-dev.txt
    
    print_step "Python dependencies installed"
}

# Function to install frontend dependencies
install_frontend_deps() {
    print_info "Installing frontend dependencies..."
    
    cd frontend
    npm install
    cd ..
    
    print_step "Frontend dependencies installed"
}

# Function to start Docker services
start_docker_services() {
    print_header "Starting Docker Services"
    
    echo -e "${CYAN}Choose deployment mode:${NC}"
    echo "1) Development (with hot reloading)"
    echo "2) Production (optimized build)"
    echo
    echo -n -e "${PURPLE}Select mode (1-2, default: 1): ${NC}"
    read deployment_mode
    
    case $deployment_mode in
        2)
            print_info "Starting production deployment..."
            docker-compose -f docker-compose.prod.yml down --remove-orphans
            docker-compose -f docker-compose.prod.yml up --build -d
            
            print_info "Waiting for services to start..."
            sleep 30
            
            # Check service health
            if docker-compose -f docker-compose.prod.yml exec backend curl -f http://localhost:8000/health > /dev/null 2>&1; then
                print_success "Production services started successfully!"
                echo -e "${GREEN}Access your application at: http://localhost:80${NC}"
            else
                print_error "Service health check failed. Check logs with: docker-compose -f docker-compose.prod.yml logs"
            fi
            ;;
        *)
            print_info "Starting development environment..."
            docker-compose -f docker-compose.dev.yml down --remove-orphans
            docker-compose -f docker-compose.dev.yml up --build -d
            
            print_info "Waiting for services to start..."
            sleep 30
            
            print_success "Development services started successfully!"
            echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
            echo -e "${GREEN}Backend API: http://localhost:8000${NC}"
            echo -e "${GREEN}API Docs: http://localhost:8000/docs${NC}"
            ;;
    esac
    
    echo
    print_info "View logs with: docker-compose logs -f"
    print_info "Stop services with: docker-compose down"
}

# Function to start manual services
start_manual_services() {
    print_header "Manual Service Startup Instructions"
    
    echo -e "${CYAN}To start the AI Trading Assistant manually, run these commands in separate terminals:${NC}"
    echo
    echo -e "${YELLOW}Terminal 1 - Redis Server:${NC}"
    echo "redis-server"
    echo
    echo -e "${YELLOW}Terminal 2 - Celery Worker:${NC}"
    echo "source venv/bin/activate"
    echo "celery -A etrade_python_client.services.celery_app worker --loglevel=info"
    echo
    echo -e "${YELLOW}Terminal 3 - Celery Beat:${NC}"
    echo "source venv/bin/activate"
    echo "celery -A etrade_python_client.services.celery_app beat --loglevel=info"
    echo
    echo -e "${YELLOW}Terminal 4 - Backend API:${NC}"
    echo "source venv/bin/activate"
    echo "python run_server.py"
    echo
    echo -e "${YELLOW}Terminal 5 - Frontend:${NC}"
    echo "cd frontend && npm start"
    echo
    echo -e "${GREEN}Once all services are running:${NC}"
    echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
    echo -e "${GREEN}Backend API: http://localhost:8000${NC}"
    echo -e "${GREEN}API Docs: http://localhost:8000/docs${NC}"
    
    echo
    echo -n -e "${PURPLE}Do you want to start Redis server now? (y/N): ${NC}"
    read start_redis
    
    if [[ $start_redis =~ ^[Yy]$ ]]; then
        if command_exists redis-server; then
            print_info "Starting Redis server in background..."
            redis-server --daemonize yes
            print_step "Redis server started"
        else
            print_error "Redis server not found. Please install Redis first."
        fi
    fi
}

# Function to run configuration validation
validate_configuration() {
    print_header "Configuration Validation"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "Configuration file not found: $CONFIG_FILE"
        return 1
    fi
    
    # Check for required settings
    local errors=0
    
    # Check Gemini API key
        if ! grep -q "GEMINI_API_KEY = .\+" "$CONFIG_FILE"; then
        print_error "Google Gemini API key not configured"
        errors=$((errors + 1))
    else
        print_step "Google Gemini API key configured"
    fi
    
    # Check basic config structure
    if grep -q "\\[DEFAULT\\]" "$CONFIG_FILE" && \
       grep -q "\\[AI_SERVICES\\]" "$CONFIG_FILE" && \
       grep -q "\\[WEB_APP\\]" "$CONFIG_FILE"; then
        print_step "Configuration file structure is valid"
    else
        print_error "Configuration file structure is invalid"
        errors=$((errors + 1))
    fi
    
    if [ $errors -eq 0 ]; then
        print_success "Configuration validation passed!"
        return 0
    else
        print_error "Configuration validation failed with $errors errors"
        return 1
    fi
}

# Function to create helpful scripts
create_helper_scripts() {
    print_info "Creating helper scripts..."
    
    # Create start script
    cat > scripts/start.sh << 'EOF'
#!/bin/bash
# Quick start script for AI Trading Assistant

echo "🚀 Starting AI Trading Assistant..."

if [ -f "docker-compose.yml" ]; then
    echo "Using Docker..."
    docker-compose up -d
    echo "✅ Services started!"
    echo "Frontend: http://localhost:3000"
    echo "Backend: http://localhost:8000"
else
    echo "❌ Docker configuration not found"
    echo "Please run ./setup.sh first"
fi
EOF

    # Create stop script
    cat > scripts/stop.sh << 'EOF'
#!/bin/bash
# Stop script for AI Trading Assistant

echo "🛑 Stopping AI Trading Assistant..."

if [ -f "docker-compose.yml" ]; then
    docker-compose down
    echo "✅ Services stopped!"
else
    echo "❌ Docker configuration not found"
fi
EOF

    # Create logs script
    cat > scripts/logs.sh << 'EOF'
#!/bin/bash
# View logs for AI Trading Assistant

if [ -f "docker-compose.yml" ]; then
    docker-compose logs -f "$@"
else
    echo "❌ Docker configuration not found"
fi
EOF

    chmod +x scripts/*.sh
    print_step "Helper scripts created in scripts/ directory"
}

# Function to display final summary
display_summary() {
    print_header "Setup Complete! 🎉"
    
    echo -e "${GREEN}AI Trading Assistant has been successfully configured!${NC}"
    echo
    
    print_info "Configuration Summary:"
    echo -e "  • Configuration file: ${CYAN}$CONFIG_FILE${NC}"
    echo -e "  • Setup mode: ${CYAN}$SETUP_MODE${NC}"
    
    if [ "$USE_DOCKER" = true ]; then
        echo -e "  • Deployment: ${CYAN}Docker${NC}"
        echo
        print_info "Quick Commands:"
        echo -e "  • Start services: ${CYAN}./scripts/docker-dev.sh${NC}"
        echo -e "  • View logs: ${CYAN}docker-compose logs -f${NC}"
        echo -e "  • Stop services: ${CYAN}docker-compose down${NC}"
    else
        echo -e "  • Deployment: ${CYAN}Manual${NC}"
        echo
        print_info "Manual Startup Required:"
        echo -e "  • See instructions above or run: ${CYAN}./scripts/start.sh${NC}"
    fi
    
    echo
    print_info "Access Points:"
    if [ "$USE_DOCKER" = true ]; then
        echo -e "  • Frontend: ${CYAN}http://localhost:3000${NC}"
        echo -e "  • Backend API: ${CYAN}http://localhost:8000${NC}"
        echo -e "  • API Docs: ${CYAN}http://localhost:8000/docs${NC}"
    else
        echo -e "  • Frontend: ${CYAN}http://localhost:3000${NC} (after npm start)"
        echo -e "  • Backend API: ${CYAN}http://localhost:8000${NC} (after python run_server.py)"
        echo -e "  • API Docs: ${CYAN}http://localhost:8000/docs${NC}"
    fi
    
    echo
    print_info "Next Steps:"
    echo -e "  1. Open the web interface"
    echo -e "  2. Connect your E*TRADE account"
    echo -e "  3. Configure trading preferences"
    echo -e "  4. Start trading with AI assistance!"
    echo
    
    print_info "Documentation:"
    echo -e "  • Main README: ${CYAN}README.md${NC}"
    echo -e "  • Docker Guide: ${CYAN}README.Docker.md${NC}"
    echo -e "  • Configuration: ${CYAN}$CONFIG_FILE${NC}"
    
    echo
    print_success "Happy trading! 📈"
}

# Main setup flow
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --manual)
                USE_DOCKER=false
                SETUP_MODE="manual"
                shift
                ;;
            --docker)
                USE_DOCKER=true
                SETUP_MODE="docker"
                shift
                ;;
            --help)
                echo "AI Trading Assistant Setup Script"
                echo
                echo "Usage: $0 [OPTIONS]"
                echo
                echo "Options:"
                echo "  --docker    Use Docker deployment (default)"
                echo "  --manual    Use manual deployment"
                echo "  --help      Show this help message"
                echo
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Welcome message
    print_header "AI Trading Assistant Setup"
    echo -e "${CYAN}Welcome to the AI Trading Assistant setup wizard!${NC}"
    echo -e "${CYAN}This script will guide you through the complete configuration process.${NC}"
    echo
    
    # Determine setup mode if not specified
    if [ -z "$SETUP_MODE" ]; then
        echo -e "${CYAN}Choose your setup method:${NC}"
        echo "1) Docker (Recommended) - Easy setup with containers"
        echo "2) Manual - Install dependencies manually"
        echo
        echo -n -e "${PURPLE}Select setup method (1-2, default: 1): ${NC}"
        read setup_choice
        
        case $setup_choice in
            2)
                USE_DOCKER=false
                SETUP_MODE="manual"
                ;;
            *)
                USE_DOCKER=true
                SETUP_MODE="docker"
                ;;
        esac
    fi
    
    print_info "Setup mode: $SETUP_MODE"
    echo
    
    # Check requirements based on setup mode
    if [ "$USE_DOCKER" = true ]; then
        check_docker
    else
        check_manual_requirements
    fi
    
    # Create necessary directories
    create_directories
    
    # Setup configuration
    copy_config_template
    
    # Configuration wizard
    configure_etrade
    configure_ai_services
    configure_notifications
    configure_advanced
    
    # Validate configuration
    validate_configuration || {
        print_error "Configuration validation failed. Please check your settings."
        exit 1
    }
    
    # Install dependencies and start services based on mode
    if [ "$USE_DOCKER" = true ]; then
        create_helper_scripts
        start_docker_services
    else
        install_python_deps
        install_frontend_deps
        create_helper_scripts
        start_manual_services
    fi
    
    # Display summary
    display_summary
}

# Error handling
trap 'print_error "Setup failed at line $LINENO. Check the error above."' ERR

# Run main function
main "$@"