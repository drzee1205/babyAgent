import time
from collections import deque
from typing import Dict, List
from src.agents import (
    get_mistral_embedding,
    task_creation_agent,
    prioritization_agent,
    execution_agent,
    context_agent,
)
from src.database import setup_supabase_table, store_task_result, cleanup_supabase_table
from src.config import OBJECTIVE, YOUR_TABLE_NAME, YOUR_FIRST_TASK


def print_header(title: str, color: str = "\033[96m\033[1m"):
    """Print a formatted header."""
    print(f"{color}\n{'*' * 5}{title.upper()}{'*' * 5}\n\033[0m\033[0m")


def add_task(task_list: deque, task: Dict):
    """Add a task to the task list."""
    task_list.append(task)


def main():
    """Main execution loop for the autonomous task agent."""
    # Print objective
    print_header("OBJECTIVE")
    print(OBJECTIVE)

    # Set up Supabase table
    print("\n🔧 Setting up database...")
    setup_supabase_table()

    # Initialize task list
    task_list = deque([])

    # Add the first task
    first_task = {"task_id": 1, "task_name": YOUR_FIRST_TASK}
    add_task(task_list, first_task)

    # Main loop configuration
    task_id_counter = 1
    max_iterations = 10  # Prevent runaway costs
    iteration = 0

    print(f"\n🚀 Starting autonomous task agent with objective: {OBJECTIVE}")
    print(f"📊 Maximum iterations: {max_iterations}")

    while task_list and iteration < max_iterations:
        iteration += 1
        print(f"\n🔄 Iteration {iteration}/{max_iterations}")
        
        # Print current task list
        print_header("TASK LIST", "\033[95m\033[1m")
        for t in task_list:
            print(f"{t['task_id']}: {t['task_name']}")

        # Step 1: Pull the first task
        task = task_list.popleft()
        print_header("NEXT TASK", "\033[92m\033[1m")
        print(f"{task['task_id']}: {task['task_name']}")

        # Step 2: Execute task
        print("\n⚡ Executing task...")
        result = execution_agent(OBJECTIVE, task["task_name"])
        this_task_id = int(task["task_id"])
        
        print_header("TASK RESULT", "\033[93m\033[1m")
        print(result)

        # Step 3: Store result in Supabase
        print("\n💾 Storing task result...")
        enriched_result = {"data": result}
        result_id = f"result_{task['task_id']}"
        
        # Generate embedding and store
        embedding = get_mistral_embedding(result)
        success = store_task_result(str(task['task_id']), task["task_name"], result, embedding)
        
        if success:
            print("✅ Task result stored successfully")
        else:
            print("❌ Failed to store task result")

        # Step 4: Create new tasks
        print("\n🎯 Generating new tasks...")
        new_tasks = task_creation_agent(
            OBJECTIVE,
            enriched_result,
            task["task_name"],
            [t["task_name"] for t in task_list]
        )
        
        # Add new tasks to the list
        for new_task in new_tasks:
            task_id_counter += 1
            new_task.update({"task_id": task_id_counter})
            add_task(task_list, new_task)
            
        if new_tasks:
            print(f"✅ Generated {len(new_tasks)} new tasks")
        else:
            print("ℹ️  No new tasks generated")

        # Step 5: Prioritize tasks
        if task_list:
            print("\n📋 Reprioritizing tasks...")
            prioritization_agent(this_task_id, task_list, OBJECTIVE)
            print("✅ Tasks reprioritized")

        # Brief pause between iterations
        print(f"\n⏱️  Waiting 2 seconds before next iteration...")
        time.sleep(2)

    # Final summary
    print_header("EXECUTION COMPLETE", "\033[96m\033[1m")
    if iteration >= max_iterations:
        print(f"🛑 Reached maximum iterations ({max_iterations})")
    else:
        print("✅ All tasks completed")
        
    if task_list:
        print(f"\n📋 Remaining tasks: {len(task_list)}")
        for t in task_list:
            print(f"  - {t['task_name']}")
    else:
        print("\n🎉 No remaining tasks")

    print(f"\n📊 Total iterations completed: {iteration}")
    print(f"🎯 Objective: {OBJECTIVE}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Task agent stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error running task agent: {e}")
        raise
    finally:
        # Optional cleanup
        cleanup_choice = input("\n🗑️  Do you want to cleanup the database table? (y/N): ").lower().strip()
        if cleanup_choice in ['y', 'yes']:
            cleanup_supabase_table()