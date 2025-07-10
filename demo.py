#!/usr/bin/env python3
"""
Demo script to showcase different interaction modes of the Autonomous Task Agent.
This script demonstrates all available interaction methods.
"""

import os
import sys
import time
import subprocess

def print_banner():
    print("\n" + "="*60)
    print("🤖 AUTONOMOUS TASK AGENT - INTERACTION DEMO")
    print("="*60)
    print("This demo showcases the different ways you can interact")
    print("with your autonomous task agent.")
    print("="*60)

def print_mode_description(mode_num, title, description, best_for, features):
    print(f"\n🎯 MODE {mode_num}: {title}")
    print("-" * 50)
    print(f"📝 Description: {description}")
    print(f"✨ Best for: {best_for}")
    print("🛠️  Features:")
    for feature in features:
        print(f"   • {feature}")

def demo_autonomous_mode():
    print_mode_description(
        1,
        "AUTONOMOUS MODE",
        "Agent runs completely independently with minimal user intervention",
        "Production runs, testing, set-and-forget operation",
        [
            "Fully automated execution",
            "Continuous task generation and execution", 
            "Real-time progress display",
            "Error handling and recovery",
            "Configurable iteration limits"
        ]
    )
    
    print("\n💻 Command to run:")
    print("   python -m src.main")
    
    print("\n📋 How it works:")
    print("   1. Set your objective in .env file")
    print("   2. Run the command above")
    print("   3. Watch the agent execute tasks autonomously")
    print("   4. Agent stops after completing objective or reaching max iterations")
    
    choice = input("\n🤔 Would you like to see a quick demo? (y/N): ").lower().strip()
    if choice in ['y', 'yes']:
        print("\n🚀 Running autonomous mode demo...")
        # Note: In a real demo, we might run a limited version
        print("   [Demo would run here - skipping for safety]")
        print("   ✅ Autonomous mode demo completed")

def demo_interactive_mode():
    print_mode_description(
        2,
        "INTERACTIVE CLI MODE",
        "Full control with real-time interaction and task management",
        "Hands-on control, learning, experimentation",
        [
            "Pause/resume execution",
            "Approve or reject tasks",
            "Edit task descriptions",
            "Change objectives mid-run",
            "Add custom tasks",
            "Real-time statistics"
        ]
    )
    
    print("\n💻 Command to run:")
    print("   python interactive_agent.py")
    
    print("\n📋 Interactive controls:")
    print("   [c] Continue execution    [p] Pause/Resume")
    print("   [v] View tasks           [o] Change objective")
    print("   [a] Add task             [r] Remove task")
    print("   [s] Show statistics      [q] Quit")
    
    choice = input("\n🤔 Would you like to try interactive mode? (y/N): ").lower().strip()
    if choice in ['y', 'yes']:
        print("\n🎮 Starting interactive mode...")
        try:
            subprocess.run([sys.executable, "interactive_agent.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
        except KeyboardInterrupt:
            print("\n👋 Interactive mode demo ended")

def demo_web_dashboard():
    print_mode_description(
        3,
        "WEB DASHBOARD MODE",
        "Beautiful web interface accessible from any device",
        "Visual monitoring, team collaboration, remote access",
        [
            "Real-time web interface",
            "Point-and-click controls",
            "Visual progress tracking",
            "Live task queue management",
            "Activity logs with timestamps",
            "Mobile-friendly design"
        ]
    )
    
    print("\n💻 Command to run:")
    print("   python web_dashboard.py")
    print("   Then open: http://localhost:5000")
    
    print("\n🌐 Web interface features:")
    print("   • Start/Stop/Pause buttons")
    print("   • Real-time task queue display")
    print("   • Objective modification form")
    print("   • Live activity logs")
    print("   • Statistics dashboard")
    print("   • Auto-refreshing content")
    
    choice = input("\n🤔 Would you like to start the web dashboard? (y/N): ").lower().strip()
    if choice in ['y', 'yes']:
        print("\n🌐 Starting web dashboard...")
        print("📱 Open your browser to: http://localhost:5000")
        print("🔧 Press Ctrl+C to stop the server")
        try:
            subprocess.run([sys.executable, "web_dashboard.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
        except KeyboardInterrupt:
            print("\n👋 Web dashboard stopped")

def demo_test_mode():
    print_mode_description(
        4,
        "TEST MODE",
        "Comprehensive testing and validation framework",
        "Validation, debugging, troubleshooting",
        [
            "Environment configuration check",
            "API connectivity testing",
            "Component validation",
            "Mini demo execution",
            "Troubleshooting guidance"
        ]
    )
    
    print("\n💻 Command to run:")
    print("   python test_agent.py")
    
    print("\n🧪 Test components:")
    print("   ✅ Environment variables validation")
    print("   ✅ Mistral AI API connection")
    print("   ✅ Supabase database setup")
    print("   ✅ Task execution functionality")
    print("   ✅ Task creation and prioritization")
    
    choice = input("\n🤔 Would you like to run the test suite? (y/N): ").lower().strip()
    if choice in ['y', 'yes']:
        print("\n🧪 Running test suite...")
        try:
            subprocess.run([sys.executable, "test_agent.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
        except Exception as e:
            print(f"❌ Test failed: {e}")

def show_configuration_guide():
    print("\n🔧 CONFIGURATION GUIDE")
    print("-" * 50)
    print("Before running any mode, ensure your .env file is configured:")
    print()
    print("📁 Required files:")
    print("   .env (your configuration)")
    print("   .env.example (template)")
    print()
    print("🔑 Required environment variables:")
    print("   MISTRAL_API_KEY=your_api_key")
    print("   SUPABASE_URL=your_project_url")
    print("   SUPABASE_ANON_KEY=your_anon_key")
    print()
    print("🎯 Optional customization:")
    print("   OBJECTIVE=Your main goal")
    print("   YOUR_FIRST_TASK=Starting task")
    print("   YOUR_TABLE_NAME=Database table")
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("\n✅ .env file found")
    else:
        print("\n❌ .env file not found")
        print("   Copy .env.example to .env and update with your credentials")

def show_comparison_table():
    print("\n📊 INTERACTION MODE COMPARISON")
    print("-" * 80)
    print("| Feature              | Autonomous | Interactive | Web Dashboard | Test    |")
    print("|----------------------|------------|-------------|---------------|---------|")
    print("| User Control        | Minimal    | Full        | Medium        | Limited |")
    print("| Real-time Feedback  | Yes        | Yes         | Yes           | Yes     |")
    print("| Task Approval       | No         | Yes         | Planned       | No      |")
    print("| Remote Access       | No         | No          | Yes           | No      |")
    print("| Visual Interface    | CLI        | CLI         | Web           | CLI     |")
    print("| Pause/Resume        | No         | Yes         | Yes           | No      |")
    print("| Edit Tasks          | No         | Yes         | Planned       | No      |")
    print("| Mobile Friendly     | No         | No          | Yes           | No      |")
    print("| Best for Beginners  | Yes        | No          | Yes           | Yes     |")
    print("| Production Ready    | Yes        | No          | Yes           | No      |")
    print("-" * 80)

def main():
    print_banner()
    
    while True:
        print("\n🎮 INTERACTION MODE SELECTOR")
        print("-" * 30)
        print("1. 🤖 Demo Autonomous Mode")
        print("2. 💬 Demo Interactive CLI Mode") 
        print("3. 🌐 Demo Web Dashboard Mode")
        print("4. 🧪 Demo Test Mode")
        print("5. 🔧 Show Configuration Guide")
        print("6. 📊 Compare All Modes")
        print("7. 🚪 Exit Demo")
        
        choice = input("\n🎯 Select an option (1-7): ").strip()
        
        if choice == '1':
            demo_autonomous_mode()
        elif choice == '2':
            demo_interactive_mode()
        elif choice == '3':
            demo_web_dashboard()
        elif choice == '4':
            demo_test_mode()
        elif choice == '5':
            show_configuration_guide()
        elif choice == '6':
            show_comparison_table()
        elif choice == '7':
            print("\n👋 Thanks for trying the Autonomous Task Agent demo!")
            print("🚀 Ready to tackle any objective you set!")
            break
        else:
            print("❌ Invalid choice. Please select 1-7.")
        
        input("\n⏸️  Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")