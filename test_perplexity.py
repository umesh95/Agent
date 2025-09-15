#!/usr/bin/env python3
"""
Simple test to verify Perplexity integration
"""

import asyncio
from app.agent import agent

async def test_perplexity():
    """Test Perplexity API integration"""
    print("🧪 Testing Perplexity Integration")
    print("=" * 40)
    
    # Check if Perplexity client is initialized
    if agent.perplexity_client:
        print("✅ Perplexity client initialized")
        print(f"   API Key: {agent.perplexity_client.api_key[:10]}...")
        print(f"   Base URL: {agent.perplexity_client.base_url}")
    else:
        print("❌ Perplexity client not initialized")
        return False
    
    # Check available models
    models = agent.get_available_models()
    print(f"\n📋 Available models: {len(models)}")
    for model in models:
        print(f"   - {model}")
    
    # Test model determination
    provider = agent._determine_provider("sonar")
    print(f"\n🎯 Model 'sonar' maps to provider: {provider.value}")
    
    try:
        # Test a simple chat
        print(f"\n💬 Testing chat with sonar model...")
        result = await agent.process_message(
            user_message="Hello! What is 2+2?",
            model="sonar",
            temperature=0.1
        )
        
        print("✅ Chat successful!")
        print(f"   Response: {result['response'][:100]}...")
        print(f"   Model used: {result['model_used']}")
        print(f"   Conversation ID: {result['conversation_id']}")
        if result.get('usage'):
            print(f"   Token usage: {result['usage']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chat failed: {e}")
        return False

async def main():
    """Main test function"""
    success = await test_perplexity()
    
    if success:
        print(f"\n🎉 Perplexity integration test passed!")
        print("✅ Ready to start the server with: python start.py")
    else:
        print(f"\n❌ Perplexity integration test failed!")
        print("🔧 Please check your API key configuration")

if __name__ == "__main__":
    asyncio.run(main())
