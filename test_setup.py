#!/usr/bin/env python3
"""
Test setup for the Philosophical Refinement Workflow

This script tests the basic setup and configuration without running
the full workflow, useful for debugging and validation.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment setup and API key configuration."""
    print("🧪 Testing Environment Setup")
    print("-" * 40)
    
    # Load environment
    load_dotenv()
    print("✅ Environment loaded")
    
    # Check API keys
    keys_status = {}
    required_keys = {
        "OPENAI_API_KEY": "OpenAI",
        "ANTHROPIC_API_KEY": "Anthropic"
    }
    
    for key, name in required_keys.items():
        value = os.getenv(key)
        if value:
            keys_status[name] = f"✅ Set ({value[:8]}...)"
        else:
            keys_status[name] = "❌ Not set"
    
    print("\nAPI Keys Status:")
    for name, status in keys_status.items():
        print(f"  {name}: {status}")
    
    return all("✅" in status for status in keys_status.values())

def test_imports():
    """Test that all required modules can be imported."""
    print("\n🧪 Testing Module Imports")
    print("-" * 40)
    
    modules = [
        ("pydantic", "Pydantic"),
        ("agno", "Agno Framework"),
        ("models", "Local Models"),
        ("agents", "Local Agents"),
        ("workflow", "Local Workflow"),
        ("logger", "Local Logger")
    ]
    
    success = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"  {name}: ✅ Import successful")
        except ImportError as e:
            print(f"  {name}: ❌ Import failed - {str(e)}")
            success = False
        except Exception as e:
            print(f"  {name}: ⚠️  Import warning - {str(e)}")
    
    return success

def test_models():
    """Test Pydantic model creation."""
    print("\n🧪 Testing Pydantic Models")
    print("-" * 40)
    
    try:
        from models import (
            PhilosophicalStatement, Assessment, WorkflowSession,
            AphoristicorResponse, AssessorResponse
        )
        from datetime import datetime
        
        # Test model creation
        statement = PhilosophicalStatement(
            content="Test statement",
            iteration=1
        )
        print(f"  PhilosophicalStatement: ✅ Created")
        
        assessment = Assessment(
            overview="Test overview",
            strengths=["Strong logic"],
            weaknesses=["Needs clarity"],
            ranking=7,
            reasoning="Test reasoning"
        )
        print(f"  Assessment: ✅ Created")
        
        session = WorkflowSession(
            session_id="test123",
            initial_statement="Test",
            current_statement="Test"
        )
        print(f"  WorkflowSession: ✅ Created")
        
        return True
        
    except Exception as e:
        print(f"  Models: ❌ Error - {str(e)}")
        return False

def main():
    """Run all setup tests."""
    print("🧠 Thinkers Dinning - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Models", test_models)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} test failed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("🧪 TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name}: {status}")
        all_passed &= passed
    
    if all_passed:
        print(f"\n🎉 All tests passed! System ready to run.")
        print(f"Run: python main.py \"Your philosophical statement here\"")
    else:
        print(f"\n⚠️  Some tests failed. Please check configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()