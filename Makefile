# Autonomous Task Agent - Quick Commands
# Usage: make <command>

.PHONY: help install test run interactive web demo clean

# Default target
help:
	@echo "🤖 Autonomous Task Agent - Available Commands:"
	@echo ""
	@echo "📦 Setup:"
	@echo "  make install     - Install all dependencies"
	@echo "  make test        - Run test suite and validation"
	@echo ""
	@echo "🎮 Run Modes:"
	@echo "  make run         - Run autonomous mode (default)"
	@echo "  make interactive - Run interactive CLI mode"
	@echo "  make web         - Start web dashboard (http://localhost:5000)"
	@echo "  make demo        - Interactive mode selector demo"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean       - Clean Python cache and temp files"
	@echo ""
	@echo "💡 Quick Start:"
	@echo "  1. Copy .env.example to .env and add your API keys"
	@echo "  2. make install"
	@echo "  3. make test"
	@echo "  4. make run (or make interactive/web/demo)"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed successfully!"
	@echo "🔧 Next: Copy .env.example to .env and add your API keys"

# Run test suite
test:
	@echo "🧪 Running test suite..."
	python test_agent.py
	@echo "✅ Tests completed!"

# Run autonomous mode
run:
	@echo "🤖 Starting Autonomous Task Agent..."
	python -m src.main

# Run interactive CLI mode
interactive:
	@echo "💬 Starting Interactive CLI Mode..."
	python interactive_agent.py

# Start web dashboard
web:
	@echo "🌐 Starting Web Dashboard..."
	@echo "📱 Open your browser to: http://localhost:5000"
	python web_dashboard.py

# Run interactive demo
demo:
	@echo "🎮 Starting Interactive Demo..."
	python demo.py

# Clean cache files
clean:
	@echo "🧹 Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name "*.coverage" -delete 2>/dev/null || true
	@echo "✅ Cache cleaned!"

# Development helpers
dev-install:
	@echo "🔧 Installing development dependencies..."
	pip install -r requirements.txt
	pip install flask-cors ipython jupyter
	@echo "✅ Development environment ready!"

# Docker commands
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t autonomous-task-agent .
	@echo "✅ Docker image built!"

docker-run:
	@echo "🐳 Running Docker container..."
	docker run --env-file .env autonomous-task-agent

# Quick validation
validate:
	@echo "🔍 Quick validation check..."
	@python -c "from src.config import OBJECTIVE; print(f'✅ Objective: {OBJECTIVE}')" 2>/dev/null || echo "❌ Configuration issue - check your .env file"
	@python -c "import mistralai; print('✅ Mistral AI library available')" 2>/dev/null || echo "❌ Missing mistralai - run 'make install'"
	@python -c "import supabase; print('✅ Supabase library available')" 2>/dev/null || echo "❌ Missing supabase - run 'make install'"
	@echo "🎯 Run 'make test' for comprehensive validation"