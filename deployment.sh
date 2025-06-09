#!/bin/bash

set -e

echo "🚀 TalentScout AI Hiring Assistant - Deployment Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_header "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_status "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is required but not installed"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_header "Checking pip installation..."
    if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        print_status "pip found"
    else
        print_error "pip is required but not installed"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_header "Creating virtual environment..."
    if [ ! -d "hiring_assistant_env" ]; then
        python3 -m venv hiring_assistant_env
        print_status "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_header "Activating virtual environment..."
    source hiring_assistant_env/bin/activate
    print_status "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_header "Installing dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        print_status "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Check for API key
check_api_key() {
    print_header "Checking for API key configuration..."
    if [ -f ".env" ]; then
        print_status ".env file found"
    else
        print_warning ".env file not found"
        echo "Creating .env template..."
        cp .env.example .env 2>/dev/null || echo "GEMINI_API_KEY=your_api_key_here" > .env
        print_warning "Please edit .env file and add your Gemini API key"
    fi
}

# Run local deployment
run_local() {
    print_header "Starting local deployment..."
    print_status "Application will be available at: http://localhost:8501"
    print_status "Press Ctrl+C to stop the application"
    echo ""
    streamlit run app.py
}

# Docker deployment functions
build_docker() {
    print_header "Building Docker image..."
    if command -v docker &> /dev/null; then
        docker build -t talentscout-hiring-assistant .
        print_status "Docker image built successfully"
    else
        print_error "Docker is not installed"
        exit 1
    fi
}

run_docker() {
    print_header "Running Docker container..."
    docker run -p 8501:8501 --env-file .env talentscout-hiring-assistant
}

# Cloud deployment helpers
deploy_streamlit_cloud() {
    print_header "Preparing for Streamlit Cloud deployment..."
    print_status "1. Push your code to GitHub"
    print_status "2. Go to https://share.streamlit.io/"
    print_status "3. Connect your GitHub repository"
    print_status "4. Add your GEMINI_API_KEY to secrets"
    print_status "5. Deploy!"
}

# Main deployment options
show_menu() {
    echo ""
    echo "Choose deployment option:"
    echo "1) Local Development (Recommended for testing)"
    echo "2) Docker Container"
    echo "3) Prepare for Streamlit Cloud"
    echo "4) Exit"
    echo ""
}

# Main execution
main() {
    print_status "Starting deployment process..."
    
    # Basic checks
    check_python
    check_pip
    
    # Setup
    create_venv
    activate_venv
    install_dependencies
    check_api_key
    
    # Show deployment options
    while true; do
        show_menu
        read -p "Enter your choice (1-4): " choice
        
        case $choice in
            1)
                run_local
                break
                ;;
            2)
                build_docker
                run_docker
                break
                ;;
            3)
                deploy_streamlit_cloud
                break
                ;;
            4)
                print_status "Deployment cancelled"
                break
                ;;
            *)
                print_error "Invalid option. Please choose 1-4."
                ;;
        esac
    done
}

# Run main function
main "$@"