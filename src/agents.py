from typing import Dict, List
from collections import deque
from mistralai import Mistral
from src.config import MISTRAL_API_KEY, supabase
import numpy as np

mistral_client = Mistral(api_key=MISTRAL_API_KEY)


def get_mistral_embedding(text: str) -> List[float]:
    """Generate embeddings using Mistral's embedding model."""
    try:
        text = text.replace("\n", " ")
        response = mistral_client.embeddings.create(
            model="mistral-embed",
            inputs=[text]
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Error generating embedding: {e}")
        return [0.0] * 1024  # Fallback to zero vector


def task_creation_agent(objective: str, result: Dict, task_description: str, task_list: List[str]) -> List[Dict]:
    """Generate new tasks based on the objective and previous results."""
    prompt = f"""You are a task creation AI that helps achieve objectives through systematic task generation.

OBJECTIVE: {objective}

LAST COMPLETED TASK: {task_description}
TASK RESULT: {result}

CURRENT INCOMPLETE TASKS:
{chr(10).join([f"- {task}" for task in task_list]) if task_list else "- None"}

Based on the objective and the result of the last completed task, create 2-4 NEW specific, actionable tasks that will help achieve the objective. 

Requirements:
- Tasks must be concrete and actionable
- Tasks should not duplicate existing incomplete tasks
- Tasks should build upon the result of the completed task
- Focus on the most important next steps

Return only the task descriptions, one per line, without numbers or bullets."""

    try:
        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=200
        )
        
        new_tasks_text = response.choices[0].message.content.strip()
        new_tasks = [line.strip() for line in new_tasks_text.split('\n') if line.strip()]
        
        return [{"task_name": task_name} for task_name in new_tasks if task_name]
    except Exception as e:
        print(f"❌ Error in task_creation_agent: {e}")
        return []


def prioritization_agent(this_task_id: int, task_list: deque, objective: str):
    """Reprioritize the task list based on the objective."""
    if not task_list:
        return
        
    task_names = [t["task_name"] for t in task_list]
    next_task_id = int(this_task_id) + 1
    
    prompt = f"""You are a task prioritization AI. Your goal is to reorder tasks to best achieve the objective.

OBJECTIVE: {objective}

CURRENT TASKS TO PRIORITIZE:
{chr(10).join([f"{i+next_task_id}. {task}" for i, task in enumerate(task_names)])}

Reorder these tasks by priority to best achieve the objective. Consider:
- Which tasks provide the most value toward the objective
- Dependencies between tasks
- Logical sequence of execution

Return the reordered tasks in the exact format:
{next_task_id}. [first task]
{next_task_id + 1}. [second task]
etc.

Use the exact task descriptions provided above."""

    try:
        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        new_tasks_text = response.choices[0].message.content.strip()
        new_tasks = new_tasks_text.split('\n')
        
        task_list.clear()
        for task_string in new_tasks:
            task_string = task_string.strip()
            if '. ' in task_string:
                task_parts = task_string.split(".", 1)
                if len(task_parts) == 2:
                    task_id = task_parts[0].strip()
                    task_name = task_parts[1].strip()
                    if task_name:  # Only add non-empty tasks
                        task_list.append({"task_id": task_id, "task_name": task_name})
    except Exception as e:
        print(f"❌ Error in prioritization_agent: {e}")


def execution_agent(objective: str, task: str) -> str:
    """Execute a specific task toward the objective."""
    context = context_agent(query=objective, n=5)
    context_text = "\n".join([f"- {item}" for item in context]) if context else "No previous context available."
    
    prompt = f"""You are an AI agent executing a specific task to achieve an objective.

OBJECTIVE: {objective}

CURRENT TASK: {task}

RELEVANT CONTEXT FROM PREVIOUS TASKS:
{context_text}

Execute this task thoroughly and provide a detailed result. Your response should:
- Directly address the task requirements
- Be specific and actionable
- Build upon the context when relevant
- Contribute meaningfully toward the objective

TASK EXECUTION:"""

    try:
        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Error in execution_agent: {e}")
        return f"Task execution failed due to error: {str(e)}"


def context_agent(query: str, n: int) -> List[str]:
    """Retrieve relevant context from previous task results."""
    try:
        query_embedding = get_mistral_embedding(query)
        response = supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_count": n,
                "filter": {}
            }
        ).execute()
        
        if response.data:
            sorted_results = sorted(response.data, key=lambda x: x.get("similarity", 0), reverse=True)
            return [item["metadata"].get("task", "") for item in sorted_results 
                   if item.get("metadata") and item["metadata"].get("task")]
        return []
    except Exception as e:
        print(f"❌ Error in context_agent: {e}")
        return []