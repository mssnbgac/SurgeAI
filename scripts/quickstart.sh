#!/bin/bash

echo "🚀 SurgeAI Trading Agent - Quick Start"
echo "======================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
    exit 1
fi

# Install Node dependencies
echo ""
echo "📦 Installing Node.js dependencies..."
npm install

# Install Python dependencies
echo ""
echo "🐍 Installing Python dependencies..."
cd agent
pip install -r requirements.txt
cd ..

# Compile contracts
echo ""
echo "🔨 Compiling smart contracts..."
npx hardhat compile

# Run tests
echo ""
echo "🧪 Running tests..."
npx hardhat test

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your private key and RPC URL"
echo "2. Deploy contracts: npm run deploy:testnet"
echo "3. Start the agent: cd agent && python main.py"
echo "4. Start the frontend: cd frontend && npm run dev"
