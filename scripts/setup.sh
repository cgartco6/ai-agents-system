#!/bin/bash

echo "🤖 Setting up Advanced AI System..."

# Create virtual environment
python3 -m venv ai_system_env
source ai_system_env/bin/activate

# Install dependencies
pip install --upgrade pip

# Core AI/ML libraries
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers datasets accelerate
pip install openai anthropic
pip install langchain langchain-community langchain-openai

# Additional dependencies
pip install asyncio aiohttp websockets
pip install numpy pandas scikit-learn
pip install psutil GPUtil
pip install pyyaml jinja2
pip install requests beautifulsoup4 selenium

# Development tools
pip install jupyter ipython
pip install black flake8 pytest

# Create necessary directories
mkdir -p outputs/generated_code
mkdir -p outputs/business_plans
mkdir -p outputs/strategic_reports
mkdir -p logs
mkdir -p data/training
mkdir -p data/knowledge_base

echo "✅ Setup complete! Activate with: source ai_system_env/bin/activate"
echo "🚀 Run with: python scripts/run_system.py"
