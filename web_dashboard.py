#!/usr/bin/env python3
"""
Simple web dashboard for the Autonomous Task Agent.
Provides a web interface for monitoring and controlling the agent.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from collections import deque
import json
import os
import sys
import threading
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents import (
    get_mistral_embedding,
    task_creation_agent,
    prioritization_agent,
    execution_agent,
)
from src.database import setup_supabase_table, store_task_result
from src.config import OBJECTIVE, YOUR_FIRST_TASK

app = Flask(__name__)

# Global agent state
class AgentState:
    def __init__(self):
        self.task_list = deque([])
        self.task_id_counter = 1
        self.objective = OBJECTIVE
        self.is_running = False
        self.is_paused = False
        self.iteration = 0
        self.max_iterations = 10
        self.current_task = None
        self.last_result = None
        self.logs = []
        self.completed_tasks = []
        self.pending_approval = None
        self.approval_required = True
        self.session_history = []
        self.start_time = None
        
    def add_log(self, message, level="info"):
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append({
            "timestamp": timestamp,
            "message": message,
            "level": level
        })
        # Keep only last 50 logs
        if len(self.logs) > 50:
            self.logs.pop(0)

agent_state = AgentState()

# HTML template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Task Agent Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        .header { 
            background: linear-gradient(45deg, #1e3c72, #2a5298); 
            color: white; 
            padding: 30px; 
            text-align: center; 
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .content { padding: 30px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        .card { 
            background: #f8f9fa; 
            border-radius: 10px; 
            padding: 25px; 
            border-left: 5px solid #007bff;
        }
        .card h3 { color: #333; margin-bottom: 15px; font-size: 1.3em; }
        .status { 
            display: inline-block; 
            padding: 8px 15px; 
            border-radius: 20px; 
            font-weight: bold; 
            margin: 5px 0; 
        }
        .running { background: #d4edda; color: #155724; }
        .paused { background: #fff3cd; color: #856404; }
        .stopped { background: #f8d7da; color: #721c24; }
        .btn { 
            padding: 12px 25px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 1em; 
            margin: 5px; 
            transition: all 0.3s;
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: #212529; }
        .btn-danger { background: #dc3545; color: white; }
        .task-list { max-height: 300px; overflow-y: auto; }
        .task-item { 
            background: white; 
            margin: 10px 0; 
            padding: 15px; 
            border-radius: 8px; 
            border-left: 4px solid #28a745;
        }
        .logs { 
            max-height: 200px; 
            overflow-y: auto; 
            background: #2d3748; 
            color: #e2e8f0; 
            padding: 15px; 
            border-radius: 8px; 
            font-family: 'Courier New', monospace;
        }
        .log-entry { margin: 2px 0; }
        .objective-form { margin: 20px 0; }
        .objective-form input { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #e2e8f0; 
            border-radius: 8px; 
            font-size: 1em;
        }
        .stats { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
            gap: 15px; 
            margin: 20px 0; 
        }
        .stat { 
            text-align: center; 
            padding: 20px; 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            border-radius: 10px; 
        }
        .stat-value { font-size: 2em; font-weight: bold; }
        .stat-label { font-size: 0.9em; opacity: 0.9; }
    </style>
    <script>
        function updateDashboard() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').textContent = data.status;
                    document.getElementById('status').className = 'status ' + data.status.toLowerCase();
                    document.getElementById('objective').textContent = data.objective;
                    document.getElementById('iteration').textContent = data.iteration;
                    document.getElementById('tasks-count').textContent = data.tasks_count;
                    
                    // Update task list
                    const taskList = document.getElementById('task-list');
                    taskList.innerHTML = '';
                    data.tasks.forEach(task => {
                        const div = document.createElement('div');
                        div.className = 'task-item';
                        div.innerHTML = `<strong>#${task.task_id}</strong>: ${task.task_name}`;
                        taskList.appendChild(div);
                    });
                    
                    // Update logs
                    const logs = document.getElementById('logs');
                    logs.innerHTML = '';
                    data.logs.forEach(log => {
                        const div = document.createElement('div');
                        div.className = 'log-entry';
                        div.innerHTML = `[${log.timestamp}] ${log.message}`;
                        logs.appendChild(div);
                    });
                    logs.scrollTop = logs.scrollHeight;
                });
        }
        
        function sendCommand(command) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: command})
            }).then(() => updateDashboard());
        }
        
        function updateObjective() {
            const objective = document.getElementById('new-objective').value;
            if (objective) {
                fetch('/api/objective', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({objective: objective})
                }).then(() => {
                    updateDashboard();
                    document.getElementById('new-objective').value = '';
                });
            }
        }
        
        // Auto-refresh every 2 seconds
        setInterval(updateDashboard, 2000);
        
        // Initial load
        window.onload = updateDashboard;
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Autonomous Task Agent</h1>
            <p>Intelligent Task Management Dashboard</p>
        </div>
        
        <div class="content">
            <div class="stats">
                <div class="stat">
                    <div class="stat-value" id="iteration">0</div>
                    <div class="stat-label">Iterations</div>
                </div>
                <div class="stat">
                    <div class="stat-value" id="tasks-count">0</div>
                    <div class="stat-label">Tasks in Queue</div>
                </div>
                <div class="stat">
                    <div class="stat-value">AI</div>
                    <div class="stat-label">Powered by Mistral</div>
                </div>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>🎯 Current Status</h3>
                    <div id="status" class="status stopped">Stopped</div>
                    <br><br>
                    <strong>Objective:</strong>
                    <p id="objective">Loading...</p>
                    
                    <div style="margin-top: 20px;">
                        <button class="btn btn-success" onclick="sendCommand('start')">▶️ Start</button>
                        <button class="btn btn-warning" onclick="sendCommand('pause')">⏸️ Pause</button>
                        <button class="btn btn-danger" onclick="sendCommand('stop')">⏹️ Stop</button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📋 Task Queue</h3>
                    <div id="task-list" class="task-list">
                        Loading tasks...
                    </div>
                </div>
                
                <div class="card">
                    <h3>⚙️ Controls</h3>
                    <div class="objective-form">
                        <label><strong>Update Objective:</strong></label>
                        <input type="text" id="new-objective" placeholder="Enter new objective...">
                        <button class="btn btn-primary" onclick="updateObjective()">Update</button>
                    </div>
                    
                    <button class="btn btn-primary" onclick="sendCommand('add_task')">➕ Add Task</button>
                    <button class="btn btn-warning" onclick="sendCommand('clear_tasks')">🗑️ Clear Tasks</button>
                </div>
                
                <div class="card">
                    <h3>📜 Activity Logs</h3>
                    <div id="logs" class="logs">
                        Loading logs...
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return DASHBOARD_HTML

@app.route('/api/status')
def api_status():
    status = "Running" if agent_state.is_running else ("Paused" if agent_state.is_paused else "Stopped")
    return jsonify({
        'status': status,
        'objective': agent_state.objective,
        'iteration': agent_state.iteration,
        'tasks_count': len(agent_state.task_list),
        'tasks': [{'task_id': t['task_id'], 'task_name': t['task_name']} for t in list(agent_state.task_list)],
        'logs': agent_state.logs[-20:]  # Last 20 logs
    })

@app.route('/api/command', methods=['POST'])
def api_command():
    command = request.json.get('command')
    
    if command == 'start':
        if not agent_state.is_running:
            agent_state.is_running = True
            agent_state.is_paused = False
            agent_state.add_log("🚀 Agent started", "success")
            # Start agent in background thread
            threading.Thread(target=run_agent_background, daemon=True).start()
    
    elif command == 'pause':
        agent_state.is_paused = not agent_state.is_paused
        status = "paused" if agent_state.is_paused else "resumed"
        agent_state.add_log(f"⏸️ Agent {status}", "warning")
    
    elif command == 'stop':
        agent_state.is_running = False
        agent_state.is_paused = False
        agent_state.add_log("⏹️ Agent stopped", "error")
    
    elif command == 'clear_tasks':
        agent_state.task_list.clear()
        agent_state.add_log("🗑️ Tasks cleared", "warning")
    
    return jsonify({'success': True})

@app.route('/api/objective', methods=['POST'])
def api_objective():
    new_objective = request.json.get('objective')
    if new_objective:
        agent_state.objective = new_objective
        agent_state.add_log(f"🎯 Objective updated: {new_objective[:50]}...", "info")
    return jsonify({'success': True})

def run_agent_background():
    """Run the agent in the background."""
    agent_state.add_log("🔧 Setting up database...", "info")
    setup_supabase_table()
    
    # Add first task if none exist
    if not agent_state.task_list:
        first_task = {"task_id": 1, "task_name": YOUR_FIRST_TASK}
        agent_state.task_list.append(first_task)
        agent_state.add_log(f"📝 Added first task: {YOUR_FIRST_TASK}", "info")
    
    while agent_state.is_running and agent_state.task_list and agent_state.iteration < agent_state.max_iterations:
        if agent_state.is_paused:
            time.sleep(1)
            continue
        
        # Execute next task
        task = agent_state.task_list.popleft()
        agent_state.current_task = task
        agent_state.add_log(f"⚡ Executing: {task['task_name'][:50]}...", "info")
        
        try:
            # Execute task
            result = execution_agent(agent_state.objective, task["task_name"])
            agent_state.last_result = result
            agent_state.add_log(f"✅ Task completed: {task['task_name'][:30]}...", "success")
            
            # Store result
            embedding = get_mistral_embedding(result)
            store_task_result(str(task['task_id']), task["task_name"], result, embedding)
            
            # Generate new tasks
            new_tasks = task_creation_agent(
                agent_state.objective,
                {"data": result},
                task["task_name"],
                [t["task_name"] for t in agent_state.task_list]
            )
            
            # Add new tasks
            for new_task in new_tasks[:3]:  # Limit to 3 new tasks
                agent_state.task_id_counter += 1
                new_task.update({"task_id": agent_state.task_id_counter})
                agent_state.task_list.append(new_task)
            
            if new_tasks:
                agent_state.add_log(f"💡 Generated {len(new_tasks[:3])} new tasks", "info")
            
            # Prioritize tasks
            if len(agent_state.task_list) > 1:
                prioritization_agent(int(task["task_id"]), agent_state.task_list, agent_state.objective)
                agent_state.add_log("📋 Tasks reprioritized", "info")
            
            agent_state.iteration += 1
            time.sleep(3)  # Brief pause between tasks
            
        except Exception as e:
            agent_state.add_log(f"❌ Error executing task: {str(e)[:50]}...", "error")
            time.sleep(5)
    
    agent_state.is_running = False
    agent_state.add_log("🏁 Agent execution completed", "success")

if __name__ == '__main__':
    print("🌐 Starting Autonomous Task Agent Web Dashboard...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🔧 Use Ctrl+C to stop the server")
    
    # Initialize with first task
    first_task = {"task_id": 1, "task_name": YOUR_FIRST_TASK}
    agent_state.task_list.append(first_task)
    agent_state.add_log("🤖 Dashboard initialized", "info")
    
    app.run(debug=True, host='0.0.0.0', port=5000)