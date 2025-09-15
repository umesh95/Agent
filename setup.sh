#!/bin/bash

echo "🤖 AI Agent Setup Script"
echo "========================"

echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "📝 Setting up environment file..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
        echo "⚠️  Please edit .env and add your API keys before running the server"
    else
        echo "❌ .env.example not found"
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run: python start.py"
echo "3. Visit: http://localhost:8000/docs"
echo ""
