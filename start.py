#!/usr/bin/env python3
"""
Startup script for AI Agent API
Handles environment setup and server startup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required keys, or if API keys are hardcoded"""
    from app.config import settings
    
    # Check if we have API keys from config (hardcoded or env)
    has_openai = bool(settings.openai_api_key and not settings.openai_api_key.startswith("your_"))
    has_anthropic = bool(settings.anthropic_api_key and not settings.anthropic_api_key.startswith("your_"))
    has_perplexity = bool(settings.perplexity_api_key and not settings.perplexity_api_key.startswith("your_"))
    
    if has_openai or has_anthropic or has_perplexity:
        print("✅ API keys configured")
        if has_perplexity:
            print(f"   Perplexity API key: {settings.perplexity_api_key[:10]}...")
        if has_openai and not settings.openai_api_key.startswith("pplx-"):
            print(f"   OpenAI API key: {settings.openai_api_key[:10]}...")
        if has_anthropic:
            print(f"   Anthropic API key: {settings.anthropic_api_key[:10]}...")
        return True
    
    # If no hardcoded keys, check for .env file
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        print("⚠️  .env file not found and no API keys configured!")
        if env_example.exists():
            print("📝 Please copy .env.example to .env and add your API keys:")
            print("   cp .env.example .env")
        else:
            print("📝 Please create a .env file with your API keys")
        print("\nRequired environment variables:")
        print("   - OPENAI_API_KEY (get from https://platform.openai.com/api-keys)")
        print("   - ANTHROPIC_API_KEY (get from https://console.anthropic.com/)")
        print("   - PERPLEXITY_API_KEY (get from https://docs.perplexity.ai/)")
        print("   - At least one of the above is required")
        return False
    
    # Read .env file to check for placeholder values
    with open(env_file, 'r') as f:
        content = f.read()
    
    has_openai = "OPENAI_API_KEY=" in content and "your_openai_api_key_here" not in content
    has_anthropic = "ANTHROPIC_API_KEY=" in content and "your_anthropic_api_key_here" not in content
    has_perplexity = "PERPLEXITY_API_KEY=" in content and "your_perplexity_api_key_here" not in content
    
    if not has_openai and not has_anthropic and not has_perplexity:
        print("⚠️  No valid API keys found in .env file!")
        print("📝 Please add at least one valid API key:")
        print("   - OPENAI_API_KEY=your_actual_key_here")
        print("   - ANTHROPIC_API_KEY=your_actual_key_here")
        print("   - PERPLEXITY_API_KEY=your_actual_key_here")
        return False
    
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import openai
        import anthropic
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Please install dependencies:")
        print("   pip install -r requirements.txt")
        return False

def main():
    """Main startup function"""
    print("🚀 Starting AI Agent API Server")
    print("=" * 40)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ Dependencies OK")
    
    # Check environment
    print("🔍 Checking environment configuration...")
    if not check_env_file():
        sys.exit(1)
    print("✅ Environment OK")
    
    # Start the server
    print("🎯 Starting FastAPI server...")
    print("📍 Server will be available at: http://localhost:9000")
    print("📚 API Documentation: http://localhost:9000/docs")
    print("📖 Alternative docs: http://localhost:9000/redoc")
    print("\n🛑 Press Ctrl+C to stop the server")
    print("-" * 40)
    
    try:
        # Import and run the app
        from app.main import app
        from app.config import settings
        import uvicorn
        
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
