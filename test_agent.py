#!/usr/bin/env python3
"""
Test script for the Autonomous Task Agent.
This script allows you to test individual components or run a limited version.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import MISTRAL_API_KEY, SUPABASE_URL, OBJECTIVE
from src.agents import get_mistral_embedding, execution_agent, task_creation_agent
from src.database import setup_supabase_table


def test_environment():
    """Test if environment variables are properly configured."""
    print("🧪 Testing Environment Configuration...")
    
    tests = [
        ("Mistral API Key", MISTRAL_API_KEY, "Set"),
        ("Supabase URL", SUPABASE_URL, "Set"),
        ("Objective", OBJECTIVE, OBJECTIVE),
    ]
    
    for name, value, expected in tests:
        status = "✅" if value and value != "your_mistral_api_key_here" else "❌"
        print(f"  {status} {name}: {expected if status == '✅' else 'Not set'}")
    
    return all(value and value != "your_mistral_api_key_here" for _, value, _ in tests)


def test_mistral_embedding():
    """Test Mistral embedding generation."""
    print("\n🧪 Testing Mistral Embedding...")
    try:
        embedding = get_mistral_embedding("Test text for embedding")
        if embedding and len(embedding) == 1024:
            print("  ✅ Embedding generation successful")
            print(f"  📊 Embedding length: {len(embedding)}")
            return True
        else:
            print("  ❌ Embedding generation failed - invalid length")
            return False
    except Exception as e:
        print(f"  ❌ Embedding generation failed: {e}")
        return False


def test_task_execution():
    """Test task execution agent."""
    print("\n🧪 Testing Task Execution...")
    try:
        result = execution_agent(
            objective="Learn about artificial intelligence",
            task="Research the basics of machine learning"
        )
        if result and len(result) > 10:
            print("  ✅ Task execution successful")
            print(f"  📝 Result preview: {result[:100]}...")
            return True
        else:
            print("  ❌ Task execution failed - no meaningful result")
            return False
    except Exception as e:
        print(f"  ❌ Task execution failed: {e}")
        return False


def test_task_creation():
    """Test task creation agent."""
    print("\n🧪 Testing Task Creation...")
    try:
        new_tasks = task_creation_agent(
            objective="Learn about artificial intelligence",
            result={"data": "Machine learning is a subset of AI that focuses on algorithms."},
            task_description="Research the basics of machine learning",
            task_list=["Study neural networks", "Explore deep learning"]
        )
        if new_tasks and len(new_tasks) > 0:
            print("  ✅ Task creation successful")
            print(f"  📋 Generated {len(new_tasks)} new tasks:")
            for i, task in enumerate(new_tasks[:3], 1):
                print(f"    {i}. {task.get('task_name', 'Unknown task')}")
            return True
        else:
            print("  ❌ Task creation failed - no tasks generated")
            return False
    except Exception as e:
        print(f"  ❌ Task creation failed: {e}")
        return False


def test_database_setup():
    """Test database setup."""
    print("\n🧪 Testing Database Setup...")
    try:
        setup_supabase_table()
        print("  ✅ Database setup completed")
        return True
    except Exception as e:
        print(f"  ❌ Database setup failed: {e}")
        return False


def run_mini_agent():
    """Run a mini version of the agent with just 2 iterations."""
    print("\n🤖 Running Mini Agent (2 iterations)...")
    
    from collections import deque
    from src.main import add_task
    from src.agents import prioritization_agent
    from src.database import store_task_result
    import time
    
    # Initialize
    task_list = deque([])
    first_task = {"task_id": 1, "task_name": "Create a simple plan"}
    add_task(task_list, first_task)
    
    for iteration in range(2):
        print(f"\n🔄 Mini Iteration {iteration + 1}/2")
        
        if not task_list:
            print("  ℹ️  No more tasks")
            break
            
        # Execute task
        task = task_list.popleft()
        print(f"  📝 Executing: {task['task_name']}")
        
        result = execution_agent(OBJECTIVE, task["task_name"])
        print(f"  ✅ Result: {result[:100]}...")
        
        # Store result
        embedding = get_mistral_embedding(result)
        store_task_result(str(task['task_id']), task["task_name"], result, embedding)
        
        # Create new tasks (limit to 2)
        new_tasks = task_creation_agent(
            OBJECTIVE,
            {"data": result},
            task["task_name"],
            [t["task_name"] for t in task_list]
        )
        
        # Add only first 2 new tasks
        task_id_counter = int(task["task_id"])
        for new_task in new_tasks[:2]:
            task_id_counter += 1
            new_task.update({"task_id": task_id_counter})
            add_task(task_list, new_task)
        
        # Prioritize
        if task_list:
            prioritization_agent(int(task["task_id"]), task_list, OBJECTIVE)
        
        time.sleep(1)
    
    print("\n🎉 Mini agent completed!")


def main():
    """Main test function."""
    print("🧪 Autonomous Task Agent - Test Suite")
    print("=" * 50)
    
    # Run tests
    tests = [
        test_environment,
        test_mistral_embedding,
        test_task_execution,
        test_task_creation,
        test_database_setup,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The agent is ready to run.")
        
        # Ask if user wants to run mini agent
        try:
            choice = input("\n🤖 Run mini agent demo? (y/N): ").lower().strip()
            if choice in ['y', 'yes']:
                run_mini_agent()
        except KeyboardInterrupt:
            print("\n👋 Test completed.")
    else:
        print("❌ Some tests failed. Please check your configuration.")
        print("\n🔧 Common fixes:")
        print("  - Verify your .env file has correct API keys")
        print("  - Check your internet connection")
        print("  - Ensure Supabase project is properly configured")


if __name__ == "__main__":
    main()