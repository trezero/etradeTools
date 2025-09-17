#!/bin/bash

# Quick Start Script for AI Trading Assistant
# This script provides a fast way to start the application after initial setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

# Function to check if setup has been run
check_setup() {
    if [ ! -f "etrade_python_client/config.ini" ]; then
        print_error "Configuration file not found!"
        echo -e "${YELLOW}Please run the setup script first: ./setup.sh${NC}"
        exit 1
    fi
    
    # Validate basic configuration
    if ! grep -q "GEMINI_API_KEY = [a-zA-Z0-9]" "etrade_python_client/config.ini"; then
        print_warning "Google Gemini API key may not be configured"
        echo -e "${YELLOW}You may want to run: ./setup.sh to configure properly${NC}"
    fi
    
    print_step "Basic configuration validated"
}

# Function to start with Docker
start_docker() {
    print_header "Starting with Docker"
    
    # Check Docker availability
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker not found!"
        echo -e "${YELLOW}Please install Docker or use manual startup${NC}"
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running!"
        echo -e "${YELLOW}Please start Docker and try again${NC}"
        exit 1
    fi
    
    print_step "Docker is available"
    
    # Choose environment
    echo -e "${CYAN}Select startup mode:${NC}"
    echo "1) Development (hot reloading, debug mode)"
    echo "2) Production (optimized, stable)"
    echo
    echo -n -e "${BLUE}Choose mode (1-2, default: 1): ${NC}"
    read mode_choice
    
    case $mode_choice in
        2)
            print_info "Starting in production mode..."
            docker-compose -f docker-compose.prod.yml down --remove-orphans >/dev/null 2>&1 || true
            docker-compose -f docker-compose.prod.yml up -d --build
            
            print_info "Waiting for services to start..."
            sleep 20
            
            # Health check
            for i in {1..6}; do
                if docker-compose -f docker-compose.prod.yml exec -T backend curl -f http://localhost:8000/health >/dev/null 2>&1; then
                    break
                fi
                if [ $i -eq 6 ]; then
                    print_warning "Health check failed, but services may still be starting"
                    break
                fi
                sleep 5
            done
            
            print_success "Production environment started!"
            echo -e "${GREEN}Application: http://localhost:80${NC}"
            echo -e "${GREEN}Backend API: http://localhost:8000 (internal)${NC}"
            ;;
        *)
            print_info "Starting in development mode..."
            docker-compose -f docker-compose.dev.yml down --remove-orphans >/dev/null 2>&1 || true
            docker-compose -f docker-compose.dev.yml up -d --build
            
            print_info "Waiting for services to start..."
            sleep 15
            
            print_success "Development environment started!"
            echo -e "${GREEN}Frontend: http://localhost:3000${NC}"
            echo -e "${GREEN}Backend API: http://localhost:8000${NC}"
            echo -e "${GREEN}API Docs: http://localhost:8000/docs${NC}"
            ;;
    esac
    
    echo
    print_info "Useful commands:"
    echo -e "  • View logs: ${CYAN}docker-compose logs -f${NC}"
    echo -e "  • Stop services: ${CYAN}docker-compose down${NC}"
    echo -e "  • Restart: ${CYAN}docker-compose restart${NC}"
}

# Function to start manually
start_manual() {
    print_header "Manual Startup Guide"
    
    # Check requirements
    local missing=()
    
    if ! command -v python3 >/dev/null 2>&1; then
        missing+=("Python 3")
    fi
    
    if ! command -v node >/dev/null 2>&1; then
        missing+=("Node.js")
    fi
    
    if ! command -v redis-server >/dev/null 2>&1; then
        missing+=("Redis Server")
    fi
    
    if [ ${#missing[@]} -ne 0 ]; then
        print_error "Missing requirements: ${missing[*]}"
        echo -e "${YELLOW}Please install missing components or use Docker startup${NC}"
        exit 1
    fi
    
    print_step "All requirements available"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_warning "Python virtual environment not found"
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements-dev.txt
        print_step "Virtual environment created and dependencies installed"
    fi
    
    # Check if frontend dependencies are installed
    if [ ! -d "frontend/node_modules" ]; then
        print_warning "Frontend dependencies not installed"
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        cd frontend && npm install && cd ..
        print_step "Frontend dependencies installed"
    fi
    
    echo
    print_success "Ready for manual startup!"
    echo
    echo -e "${CYAN}Run these commands in separate terminals:${NC}"
    echo
    echo -e "${YELLOW}Terminal 1 - Redis:${NC}"
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
    echo -e "${YELLOW}Terminal 4 - Backend:${NC}"
    echo "source venv/bin/activate"
    echo "python run_server.py"
    echo
    echo -e "${YELLOW}Terminal 5 - Frontend:${NC}"
    echo "cd frontend && npm start"
    echo
    echo -e "${GREEN}Access points after startup:${NC}"
    echo -e "  • Frontend: ${CYAN}http://localhost:3000${NC}"
    echo -e "  • Backend API: ${CYAN}http://localhost:8000${NC}"
    echo -e "  • API Docs: ${CYAN}http://localhost:8000/docs${NC}"
    
    echo
    echo -n -e "${BLUE}Would you like to start Redis server now? (y/N): ${NC}"
    read start_redis
    
    if [[ $start_redis =~ ^[Yy]$ ]]; then
        if command -v redis-server >/dev/null 2>&1; then
            print_info "Starting Redis server..."
            redis-server --daemonize yes 2>/dev/null && print_step "Redis started in background" || print_warning "Redis may already be running"
        fi
    fi
}

# Function to check system status
check_status() {
    print_header "System Status Check"
    
    # Check if Docker containers are running
    if command -v docker >/dev/null 2>&1 && docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "etrade"; then
        print_step "Docker containers detected:"
        docker ps --format "table {{.Names}}\t{{.Status}}" | grep "etrade"
        echo
        
        # Check service health
        for container in etrade_backend etrade_frontend; do
            if docker ps --format "{{.Names}}" | grep -q "$container"; then
                print_step "$container is running"
            fi
        done
        
        echo
        print_info "Docker service URLs:"
        echo -e "  • Frontend: ${CYAN}http://localhost:3000${NC}"
        echo -e "  • Backend: ${CYAN}http://localhost:8000${NC}"
        
    # Check manual processes
    elif pgrep -f "run_server.py" >/dev/null || pgrep -f "npm start" >/dev/null; then
        print_step "Manual processes detected:"
        
        if pgrep -f "redis-server" >/dev/null; then
            print_step "Redis server is running"
        else
            print_warning "Redis server not detected"
        fi
        
        if pgrep -f "celery.*worker" >/dev/null; then
            print_step "Celery worker is running"
        else
            print_warning "Celery worker not detected"
        fi
        
        if pgrep -f "celery.*beat" >/dev/null; then
            print_step "Celery beat is running"
        else
            print_warning "Celery beat not detected"
        fi
        
        if pgrep -f "run_server.py" >/dev/null; then
            print_step "Backend server is running"
        else
            print_warning "Backend server not detected"
        fi
        
        if pgrep -f "npm start" >/dev/null; then
            print_step "Frontend server is running"
        else
            print_warning "Frontend server not detected"
        fi
        
    else
        print_info "No AI Trading Assistant processes detected"
        echo -e "${YELLOW}Use this script to start the application${NC}"
    fi
}

# Function to stop services
stop_services() {
    print_header "Stopping Services"
    
    # Stop Docker services
    if command -v docker >/dev/null 2>&1; then
        if docker ps --format "{{.Names}}" | grep -q "etrade"; then
            print_info "Stopping Docker containers..."
            docker-compose -f docker-compose.dev.yml down >/dev/null 2>&1 || true
            docker-compose -f docker-compose.prod.yml down >/dev/null 2>&1 || true
            docker-compose down >/dev/null 2>&1 || true
            print_step "Docker containers stopped"
        fi
    fi
    
    # Stop manual processes
    if pgrep -f "run_server.py" >/dev/null; then
        print_info "Stopping backend server..."
        pkill -f "run_server.py" || true
        print_step "Backend server stopped"
    fi
    
    if pgrep -f "celery.*worker" >/dev/null; then
        print_info "Stopping Celery worker..."
        pkill -f "celery.*worker" || true
        print_step "Celery worker stopped"
    fi
    
    if pgrep -f "celery.*beat" >/dev/null; then
        print_info "Stopping Celery beat..."
        pkill -f "celery.*beat" || true
        print_step "Celery beat stopped"
    fi
    
    # Note: We don't stop Redis or npm processes as they might be used by other applications
    
    print_success "Services stopped successfully"
}

# Main function
main() {
    case "$1" in
        "status")
            check_status
            ;;
        "stop")
            stop_services
            ;;
        "docker")
            check_setup
            start_docker
            ;;
        "manual")
            check_setup
            start_manual
            ;;
        "validate")
            if [ -f "scripts/validate-config.sh" ]; then
                ./scripts/validate-config.sh
            else
                print_error "Validation script not found"
                exit 1
            fi
            ;;
        "--help"|"-h"|"help")
            echo "AI Trading Assistant Quick Start"
            echo
            echo "Usage: $0 [COMMAND]"
            echo
            echo "Commands:"
            echo "  (no args)  Interactive startup menu"
            echo "  docker     Start with Docker"
            echo "  manual     Start manually"
            echo "  status     Check system status"
            echo "  stop       Stop all services"
            echo "  validate   Validate configuration"
            echo "  help       Show this help"
            echo
            exit 0
            ;;
        "")
            # Interactive mode
            print_header "AI Trading Assistant Quick Start"
            
            check_setup
            
            echo -e "${CYAN}What would you like to do?${NC}"
            echo "1) Start with Docker (recommended)"
            echo "2) Start manually"
            echo "3) Check system status"
            echo "4) Stop all services"
            echo "5) Validate configuration"
            echo "6) Exit"
            echo
            echo -n -e "${BLUE}Choose option (1-6): ${NC}"
            read choice
            
            case $choice in
                1) start_docker ;;
                2) start_manual ;;
                3) check_status ;;
                4) stop_services ;;
                5) 
                    if [ -f "scripts/validate-config.sh" ]; then
                        ./scripts/validate-config.sh
                    else
                        print_error "Validation script not found"
                    fi
                    ;;
                6) print_info "Goodbye!" ;;
                *) print_error "Invalid choice" ;;
            esac
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

main "$@"