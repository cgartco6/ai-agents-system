#!/bin/bash

set -e  # Exit on any error

echo "🤖 Starting Advanced AI System Setup..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
check_python() {
    log_info "Checking Python version..."
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
        log_info "Found Python $PYTHON_VERSION"
        
        # Check if version is at least 3.8
        python3 -c 'import sys; exit(0) if sys.version_info >= (3, 8) else exit(1)'
        if [ $? -eq 0 ]; then
            log_success "Python version is compatible (>= 3.8)"
        else
            log_error "Python 3.8 or higher is required"
            exit 1
        fi
    else
        log_error "Python 3 is not installed"
        exit 1
    fi
}

# Check and create virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    if [ ! -d "ai_system_env" ]; then
        python3 -m venv ai_system_env
        log_success "Virtual environment created"
    else
        log_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source ai_system_env/bin/activate
    log_success "Virtual environment activated"
}

# Upgrade pip
upgrade_pip() {
    log_info "Upgrading pip..."
    pip install --upgrade pip
    log_success "pip upgraded to latest version"
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Core AI/ML libraries
    log_info "Installing core AI/ML libraries..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    pip install transformers datasets accelerate
    pip install openai anthropic
    pip install langchain langchain-community langchain-openai
    
    # Web and API libraries
    log_info "Installing web and API libraries..."
    pip install aiohttp beautifulsoup4 requests
    pip install fastapi uvicorn
    
    # Data processing
    log_info "Installing data processing libraries..."
    pip install numpy pandas scikit-learn
    pip install matplotlib seaborn plotly
    
    # System and utilities
    log_info "Installing system and utility libraries..."
    pip install psutil GPUtil
    pip install python-dotenv
    pip install pyyaml jinja2
    pip install asyncio-mqtt redis
    
    # Development tools
    log_info "Installing development tools..."
    pip install jupyter ipython
    pip install black flake8 pytest
    pip install pre-commit
    
    # Security
    log_info "Installing security libraries..."
    pip install cryptography bcrypt
    
    log_success "All Python dependencies installed"
}

# Create directory structure
create_directories() {
    log_info "Creating directory structure..."
    
    directories=(
        "outputs/generated_code"
        "outputs/business_plans"
        "outputs/strategic_reports"
        "outputs/marketing_materials"
        "data/training"
        "data/knowledge_base"
        "data/vector_store"
        "logs/system"
        "logs/agents"
        "config"
        "models/trained"
        "models/pretrained"
        "exports"
        "backups"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "Created directory: $dir"
        else
            log_warning "Directory already exists: $dir"
        fi
    done
    
    log_success "Directory structure created"
}

# Create configuration files
create_config_files() {
    log_info "Creating configuration files..."
    
    # Main configuration file
    cat > config/system_config.yaml << 'EOF'
system:
  name: "Advanced AI Agent System"
  version: "1.0.0"
  environment: "development"
  debug: true
  log_level: "INFO"

ai_models:
  openai:
    api_key: "${OPENAI_API_KEY}"
    default_model: "gpt-4"
    temperature: 0.7
    max_tokens: 2000
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    default_model: "claude-3-sonnet-20240229"
    max_tokens: 2000
  local_models:
    enabled: false
    model_path: "models/pretrained"

agents:
  default_autonomy: "medium"
  max_concurrent_tasks: 10
  learning_enabled: true
  self_improvement: true

memory:
  vector_store:
    dimension: 384
    persistence_path: "data/vector_store/vectors.pkl"
  knowledge_base:
    database_path: "data/knowledge_base/knowledge.db"

security:
  encryption_enabled: true
  api_key_encryption: true
  data_encryption: true

monitoring:
  system_metrics: true
  agent_performance: true
  resource_tracking: true
  alerting: true

api:
  enabled: true
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["http://localhost:3000"]
EOF

    # Environment template
    cat > .env.example << 'EOF'
# AI API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database
DATABASE_URL=sqlite:///data/knowledge_base/knowledge.db

# Security
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Monitoring
LOG_LEVEL=INFO
DEBUG_MODE=false

# APIs
PAYFAST_MERCHANT_ID=your_merchant_id
PAYFAST_MERCHANT_KEY=your_merchant_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token

# System
MAX_WORKERS=5
TASK_TIMEOUT=300
EOF

    log_success "Configuration files created"
}

# Setup pre-commit hooks
setup_pre_commit() {
    log_info "Setting up pre-commit hooks..."
    
    if command -v pre-commit &>/dev/null; then
        cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
EOF

        pre-commit install
        log_success "Pre-commit hooks installed"
    else
        log_warning "pre-commit not installed, skipping hook setup"
    fi
}

# Create startup script
create_startup_script() {
    log_info "Creating startup script..."
    
    cat > start_system.sh << 'EOF'
#!/bin/bash

set -e

echo "🚀 Starting Advanced AI System..."

# Check if virtual environment exists
if [ ! -d "ai_system_env" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Activate virtual environment
source ai_system_env/bin/activate

# Check for required environment variables
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Copy .env.example to .env and configure your settings."
    echo "Using default configuration..."
fi

# Set Python path
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Run the system
python scripts/run_system.py "$@"
EOF

    chmod +x start_system.sh
    
    log_success "Startup script created"
}

# Create monitoring script
create_monitoring_script() {
    log_info "Creating monitoring script..."
    
    cat > monitor_system.sh << 'EOF'
#!/bin/bash

set -e

echo "📊 Starting System Monitor..."

# Check if virtual environment exists
if [ ! -d "ai_system_env" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Activate virtual environment
source ai_system_env/bin/activate

# Set Python path
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Run the monitor
python scripts/monitor.py "$@"
EOF

    chmod +x monitor_system.sh
    
    log_success "Monitoring script created"
}

# Display completion message
show_completion() {
    echo ""
    echo "========================================"
    log_success "Advanced AI System Setup Complete! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Copy .env.example to .env and configure your settings"
    echo "2. Activate the virtual environment: source ai_system_env/bin/activate"
    echo "3. Start the system: ./start_system.sh"
    echo "4. Monitor the system: ./monitor_system.sh"
    echo ""
    echo "Available commands:"
    echo "  ./start_system.sh      - Start the AI system"
    echo "  ./monitor_system.sh    - Monitor system performance"
    echo "  source ai_system_env/bin/activate - Activate virtual environment"
    echo ""
}

# Main setup function
main() {
    log_info "Starting Advanced AI System setup..."
    
    check_python
    setup_venv
    upgrade_pip
    install_dependencies
    create_directories
    create_config_files
    setup_pre_commit
    create_startup_script
    create_monitoring_script
    show_completion
}

# Run main function
main "$@"
