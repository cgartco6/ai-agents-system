#!/bin/bash

echo "🚀 Starting Advanced AI System with Synthetic Intelligence..."

# Check if virtual environment exists
if [ ! -d "ai_system_env" ]; then
    echo "📦 Setting up environment..."
    chmod +x scripts/setup.sh
    ./scripts/setup.sh
fi

# Activate environment
source ai_system_env/bin/activate

# Set required environment variables
export OPENAI_API_KEY="your_openai_key_here"
export ANTHROPIC_API_KEY="your_anthropic_key_here"

# Run the system
python scripts/run_system.py "$@"
