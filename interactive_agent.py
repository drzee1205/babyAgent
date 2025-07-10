#!/usr/bin/env python3
"""
Interactive CLI version of the Autonomous Task Agent.
This version allows real-time user interaction and control.
"""

import os
import sys
import time
from collections import deque
from typing import Dict, List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents import (
    get_mistral_embedding,
    task_creation_agent,
    prioritization_agent,
    execution_agent,
    context_agent,
)
from src.database import setup_supabase_table, store_task_result, cleanup_supabase_table
from src.config import OBJECTIVE, YOUR_TABLE_NAME, YOUR_FIRST_TASK


class InteractiveTaskAgent:
    def __init__(self):
        self.task_list = deque([])
        self.task_id_counter = 1
        self.objective = OBJECTIVE
        self.paused = False
        self.iteration = 0
        self.max_iterations = 10
        
    def print_header(self, title: str, color: str = "\033[96m\033[1m"):
        """Print a formatted header."""
        print(f"{color}\n{'=' * 20} {title.upper()} {'=' * 20}\n\033[0m\033[0m")
    
    def print_menu(self):
        """Display interaction menu."""
        print("\n" + "🤖 " + "=" * 50)
        print("│  AUTONOMOUS TASK AGENT - INTERACTIVE MODE     │")
        print("=" * 52)
        print("│ Commands:                                      │")
        print("│  [c] Continue execution                        │")
        print("│  [p] Pause/Resume                              │")
        print("│  [v] View current tasks                        │")
        print("│  [o] Change objective                          │")
        print("│  [a] Add custom task                           │")
        print("│  [r] Remove task                               │")
        print("│  [s] Show statistics                           │")
        print("│  [q] Quit agent                                │")
        print("=" * 52)
    
    def display_tasks(self):
        """Display current task list."""
        self.print_header("CURRENT TASK LIST", "\033[95m\033[1m")
        if not self.task_list:
            print("📝 No tasks in queue")
            return
            
        for i, task in enumerate(self.task_list, 1):
            print(f"{i}. [{task['task_id']}] {task['task_name']}")
    
    def display_stats(self):
        """Display agent statistics."""
        self.print_header("AGENT STATISTICS", "\033[93m\033[1m")
        print(f"🎯 Current Objective: {self.objective}")
        print(f"🔄 Iterations Completed: {self.iteration}")
        print(f"📋 Tasks in Queue: {len(self.task_list)}")
        print(f"🚀 Status: {'Paused' if self.paused else 'Running'}")
        print(f"⏱️  Max Iterations: {self.max_iterations}")
    
    def change_objective(self):
        """Allow user to change the objective."""
        print(f"\n🎯 Current objective: {self.objective}")
        new_objective = input("Enter new objective (or press Enter to keep current): ").strip()
        if new_objective:
            self.objective = new_objective
            print(f"✅ Objective updated to: {self.objective}")
        else:
            print("ℹ️  Objective unchanged")
    
    def add_custom_task(self):
        """Allow user to add a custom task."""
        task_name = input("Enter task description: ").strip()
        if task_name:
            self.task_id_counter += 1
            new_task = {"task_id": self.task_id_counter, "task_name": task_name}
            self.task_list.append(new_task)
            print(f"✅ Added task: {task_name}")
        else:
            print("❌ Task description cannot be empty")
    
    def remove_task(self):
        """Allow user to remove a task."""
        if not self.task_list:
            print("📝 No tasks to remove")
            return
            
        self.display_tasks()
        try:
            choice = int(input("Enter task number to remove (0 to cancel): "))
            if choice == 0:
                return
            if 1 <= choice <= len(self.task_list):
                removed_task = list(self.task_list)[choice - 1]
                # Convert deque to list, remove item, convert back
                task_list_copy = list(self.task_list)
                task_list_copy.pop(choice - 1)
                self.task_list = deque(task_list_copy)
                print(f"✅ Removed task: {removed_task['task_name']}")
            else:
                print("❌ Invalid task number")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def execute_next_task(self):
        """Execute the next task with user approval."""
        if not self.task_list:
            print("📝 No tasks to execute")
            return False
            
        # Get next task
        task = self.task_list.popleft()
        
        self.print_header("NEXT TASK", "\033[92m\033[1m")
        print(f"🎯 Task ID: {task['task_id']}")
        print(f"📝 Description: {task['task_name']}")
        print(f"🎪 Objective: {self.objective}")
        
        # Ask for approval
        while True:
            choice = input("\n🤔 Execute this task? [y]es/[n]o/[e]dit/[s]kip: ").lower().strip()
            
            if choice in ['y', 'yes', '']:
                break
            elif choice in ['n', 'no']:
                # Put task back at front
                self.task_list.appendleft(task)
                print("❌ Task execution cancelled")
                return False
            elif choice in ['e', 'edit']:
                new_description = input("Enter new task description: ").strip()
                if new_description:
                    task['task_name'] = new_description
                    print(f"✅ Task updated: {new_description}")
                break
            elif choice in ['s', 'skip']:
                print("⏭️  Task skipped")
                return True
            else:
                print("❌ Please enter y, n, e, or s")
        
        # Execute task
        print("\n⚡ Executing task...")
        result = execution_agent(self.objective, task["task_name"])
        
        self.print_header("TASK RESULT", "\033[93m\033[1m")
        print(result)
        
        # Store result
        print("\n💾 Storing result...")
        embedding = get_mistral_embedding(result)
        success = store_task_result(str(task['task_id']), task["task_name"], result, embedding)
        
        if success:
            print("✅ Result stored successfully")
        else:
            print("❌ Failed to store result")
        
        # Generate new tasks
        self.generate_new_tasks(task, result)
        
        self.iteration += 1
        return True
    
    def generate_new_tasks(self, completed_task: Dict, result: str):
        """Generate new tasks based on completed task."""
        print("\n🎯 Generating new tasks...")
        
        new_tasks = task_creation_agent(
            self.objective,
            {"data": result},
            completed_task["task_name"],
            [t["task_name"] for t in self.task_list]
        )
        
        if not new_tasks:
            print("ℹ️  No new tasks generated")
            return
        
        print(f"💡 Generated {len(new_tasks)} new tasks:")
        for i, task in enumerate(new_tasks, 1):
            print(f"  {i}. {task['task_name']}")
        
        # Ask user to approve new tasks
        approved_tasks = []
        for task in new_tasks:
            choice = input(f"\n➕ Add task '{task['task_name'][:50]}...'? [y]/n: ").lower().strip()
            if choice in ['', 'y', 'yes']:
                self.task_id_counter += 1
                task.update({"task_id": self.task_id_counter})
                approved_tasks.append(task)
                self.task_list.append(task)
                print("✅ Task added")
            else:
                print("❌ Task rejected")
        
        # Prioritize tasks
        if approved_tasks and len(self.task_list) > 1:
            choice = input("\n📋 Reprioritize tasks? [y]/n: ").lower().strip()
            if choice in ['', 'y', 'yes']:
                print("🔄 Reprioritizing tasks...")
                prioritization_agent(int(completed_task["task_id"]), self.task_list, self.objective)
                print("✅ Tasks reprioritized")
    
    def run(self):
        """Main interactive loop."""
        print("🤖 Autonomous Task Agent - Interactive Mode")
        print("=" * 50)
        
        # Setup
        print("🔧 Setting up database...")
        setup_supabase_table()
        
        # Add first task
        first_task = {"task_id": 1, "task_name": YOUR_FIRST_TASK}
        self.task_list.append(first_task)
        
        print(f"\n🎯 Objective: {self.objective}")
        print(f"📝 First Task: {YOUR_FIRST_TASK}")
        
        # Main loop
        while self.task_list and self.iteration < self.max_iterations:
            if not self.paused:
                # Show current status
                self.display_tasks()
                self.display_stats()
                
                # Show menu
                self.print_menu()
                
                # Get user choice
                choice = input("\n🎮 Enter command: ").lower().strip()
                
                if choice in ['c', 'continue', '']:
                    if self.execute_next_task():
                        print(f"\n⏱️  Iteration {self.iteration} complete")
                        time.sleep(1)
                elif choice in ['p', 'pause']:
                    self.paused = not self.paused
                    status = "Paused" if self.paused else "Resumed"
                    print(f"⏸️  Agent {status}")
                elif choice in ['v', 'view']:
                    self.display_tasks()
                elif choice in ['o', 'objective']:
                    self.change_objective()
                elif choice in ['a', 'add']:
                    self.add_custom_task()
                elif choice in ['r', 'remove']:
                    self.remove_task()
                elif choice in ['s', 'stats']:
                    self.display_stats()
                elif choice in ['q', 'quit']:
                    print("👋 Stopping agent...")
                    break
                else:
                    print("❌ Unknown command. Please try again.")
            else:
                choice = input("⏸️  Agent paused. Press [c] to continue or [q] to quit: ").lower().strip()
                if choice in ['c', 'continue']:
                    self.paused = False
                    print("▶️  Agent resumed")
                elif choice in ['q', 'quit']:
                    break
        
        # Final summary
        self.print_header("SESSION COMPLETE", "\033[96m\033[1m")
        if self.iteration >= self.max_iterations:
            print(f"🛑 Reached maximum iterations ({self.max_iterations})")
        else:
            print("✅ Session completed")
        
        if self.task_list:
            print(f"\n📋 Remaining tasks: {len(self.task_list)}")
            for t in self.task_list:
                print(f"  - {t['task_name']}")
        
        print(f"\n📊 Total iterations: {self.iteration}")
        
        # Cleanup option
        try:
            cleanup_choice = input("\n🗑️  Cleanup database? [y]/n: ").lower().strip()
            if cleanup_choice in ['', 'y', 'yes']:
                cleanup_supabase_table()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")


if __name__ == "__main__":
    try:
        agent = InteractiveTaskAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\n\n⏹️  Interactive agent stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error running interactive agent: {e}")
        raise