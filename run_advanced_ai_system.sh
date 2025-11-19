
## Final Setup and Run Command

Create this comprehensive startup script:

### run_advanced_ai_system.sh
```bash
#!/bin/bash

echo "🚀 ADVANCED AI SYSTEM - COMPLETE DEPLOYMENT"
echo "==========================================="

# Check if setup has been run
if [ ! -d "ai_system_env" ]; then
    echo "📦 First-time setup detected..."
    echo "This will take 5-10 minutes depending on your internet connection"
    chmod +x scripts/setup.sh
    ./scripts/setup.sh
    
    if [ $? -ne 0 ]; then
        echo "❌ Setup failed. Please check the errors above."
        exit 1
    fi
fi

# Check for environment configuration
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found."
    echo "Creating from template... Please configure your settings."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys and configuration"
    echo "Then run this script again."
    exit 1
fi

# Activate virtual environment
source ai_system_env/bin/activate

# Set Python path
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# Check for required API keys
if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: No AI API keys found in environment"
    echo "The system will work but with limited capabilities"
    echo "Add your keys to the .env file for full functionality"
fi

echo "✅ Environment ready"
echo "🤖 Starting Advanced AI System..."

# Determine run mode
if [ "$1" == "--monitor" ]; then
    echo "📊 Starting in Monitor Mode..."
    python scripts/monitor.py
elif [ "$1" == "--report" ]; then
    echo "📈 Generating System Report..."
    python scripts/monitor.py --report --duration 24
elif [ "$1" == "--interactive" ]; then
    echo "💬 Starting Interactive Mode..."
    python scripts/run_system.py --interactive
else
    echo "🎯 Starting Full System..."
    python scripts/run_system.py "$@"
fi
