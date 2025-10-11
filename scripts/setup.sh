#!/bin/bash

# Thales Cyber Shield Setup Script
# For Thales GenTech India Hackathon 2025

echo "🛡️  Setting up Thales Cyber Shield..."
echo "   AI-Powered Threat Intelligence & Response System"
echo ""

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* && "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for Linux/macOS. For Windows, use WSL2."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p models data/sample_data logs

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔄 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check Node.js for frontend
if command -v npm &> /dev/null; then
    echo "🔄 Installing frontend dependencies..."
    npm install
    echo "✅ Frontend dependencies installed"
else
    echo "⚠️  Node.js not found. Frontend dashboard will not be available."
    echo "   Install Node.js from https://nodejs.org/ to enable the dashboard"
fi

# Create sample configuration
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment configuration..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your API keys."
else
    echo "✅ Environment configuration exists"
fi

# Check Docker
if command -v docker &> /dev/null; then
    echo "🐳 Docker found. You can use 'docker-compose up' to run the full stack."
else
    echo "⚠️  Docker not found. Install Docker to use containerized deployment."
fi

# Create sample data
echo "📊 Creating sample threat data..."
cat > data/sample_data/sample_threats.json << 'EOF'
[
  {
    "timestamp": "2025-10-07T12:00:00Z",
    "threat_type": "APT36_TRANSPARENT_TRIBE",
    "source_ip": "203.0.113.100",
    "target_ip": "10.0.0.50",
    "confidence": 0.85,
    "description": "APT36 credential harvesting attempt detected"
  },
  {
    "timestamp": "2025-10-07T12:05:00Z", 
    "threat_type": "RANSOMWARE_DOUBLE_EXTORTION",
    "source_ip": "198.51.100.200",
    "target_ip": "10.0.0.75",
    "confidence": 0.92,
    "description": "Ransomware encryption and exfiltration detected"
  }
]
EOF

echo ""
echo "🎉 Thales Cyber Shield setup complete!"
echo ""
echo "🚀 Quick Start:"
echo "   1. Edit .env file with your API keys"
echo "   2. Run: python src/main.py"
echo "   3. Open browser: http://localhost:8000/docs"
echo ""
echo "🐳 Docker deployment:"
echo "   1. Run: docker-compose up -d"
echo "   2. Dashboard: http://localhost:3000"
echo "   3. API docs: http://localhost:8000/docs"
echo ""
echo "☸️  Kubernetes deployment:"
echo "   1. Run: kubectl apply -f deployment/k8s/"
echo "   2. Check: kubectl get pods -n thales-cyber-shield"
echo ""
echo "📚 Documentation: docs/README.md"
echo "🛡️  Built for Thales GenTech India Hackathon 2025"
echo "    Protecting India's Digital Future!"
