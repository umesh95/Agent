#!/usr/bin/env python3
"""
Simple test client for the AI Agent API
Run this script to test the basic functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:9000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Available models: {len(data['available_models'])}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:9000")
        return False

def test_models():
    """Test models endpoint"""
    print("\nTesting models endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/models")
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Available models: {models}")
            return models
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error testing models: {e}")
        return []

def test_chat(model=None):
    """Test chat endpoint"""
    print(f"\nTesting chat endpoint with model: {model or 'default'}...")
    
    chat_request = {
        "message": "Hello! Can you tell me a short joke?",
        "temperature": 0.7
    }
    
    if model:
        chat_request["model"] = model
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=chat_request)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat successful!")
            print(f"   Response: {data['response'][:100]}...")
            print(f"   Model used: {data['model_used']}")
            print(f"   Conversation ID: {data['conversation_id']}")
            if data.get('usage'):
                print(f"   Token usage: {data['usage']}")
            return data['conversation_id']
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing chat: {e}")
        return None

def test_conversation_continuity(conversation_id):
    """Test conversation continuity"""
    print(f"\nTesting conversation continuity...")
    
    chat_request = {
        "message": "What was my previous message about?",
        "conversation_id": conversation_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=chat_request)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conversation continuity works!")
            print(f"   Response: {data['response'][:150]}...")
            return True
        else:
            print(f"❌ Conversation continuity failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing conversation continuity: {e}")
        return False

def test_conversation_management(conversation_id):
    """Test conversation management endpoints"""
    print(f"\nTesting conversation management...")
    
    try:
        # Get conversation summary
        response = requests.get(f"{BASE_URL}/conversations/{conversation_id}")
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Conversation summary retrieved")
            print(f"   Messages: {summary['message_count']}")
        
        # Get all conversations
        response = requests.get(f"{BASE_URL}/conversations")
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Active conversations: {len(conversations)}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing conversation management: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 AI Agent API Test Client")
    print("=" * 40)
    
    # Test basic connectivity
    if not test_health():
        print("\n❌ Basic connectivity failed. Please check:")
        print("   1. Server is running: python main.py")
        print("   2. At least one API key is configured in .env")
        return
    
    # Test available models
    models = test_models()
    if not models:
        print("\n❌ No models available. Please check your API keys in .env")
        return
    
    # Test chat with default model
    conversation_id = test_chat()
    if not conversation_id:
        print("\n❌ Chat test failed")
        return
    
    # Test conversation continuity
    test_conversation_continuity(conversation_id)
    
    # Test conversation management
    test_conversation_management(conversation_id)
    
    # Test with specific model if available
    if len(models) > 1:
        test_chat(models[1])
    
    print("\n🎉 All tests completed!")
    print("\nNext steps:")
    print("   1. Visit http://localhost:9000/docs for interactive API documentation")
    print("   2. Try the chat endpoint with different models and parameters")
    print("   3. Explore conversation management features")

if __name__ == "__main__":
    main()
