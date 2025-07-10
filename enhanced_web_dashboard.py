#!/usr/bin/env python3
"""
Enhanced Web Dashboard for the Autonomous Task Agent.
Features: Real-time interface, task approval, historical sessions, visual tracking.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from collections import deque
import json
import os
import sys
import threading
import time
import datetime
from pathlib import Path

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

# Enhanced Agent State with full feature support
class EnhancedAgentState:
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
        self.execution_stats = {
            'total_tasks_completed': 0,
            'total_tasks_generated': 0,
            'success_rate': 100,
            'avg_execution_time': 0
        }
        
    def add_log(self, message, level="info"):
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append({
            "timestamp": timestamp,
            "message": message,
            "level": level,
            "full_timestamp": datetime.datetime.now().isoformat()
        })
        # Keep only last 100 logs
        if len(self.logs) > 100:
            self.logs.pop(0)
    
    def save_session(self):
        """Save current session to history."""
        if self.start_time:
            session = {
                'start_time': self.start_time,
                'end_time': datetime.datetime.now().isoformat(),
                'objective': self.objective,
                'iterations': self.iteration,
                'completed_tasks': self.completed_tasks.copy(),
                'stats': self.execution_stats.copy(),
                'logs': self.logs.copy()
            }
            self.session_history.append(session)
            # Keep only last 10 sessions
            if len(self.session_history) > 10:
                self.session_history.pop(0)

agent_state = EnhancedAgentState()

# Enhanced HTML template with all features
ENHANCED_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonomous Task Agent - Enhanced Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 15px;
            color: #333;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 20px; 
            overflow: hidden;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        }
        .header { 
            background: linear-gradient(135deg, #1e3c72, #2a5298); 
            color: white; 
            padding: 25px 30px; 
            position: relative;
            overflow: hidden;
        }
        .header::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="80" r="1.5" fill="rgba(255,255,255,0.1)"/></svg>');
        }
        .header-content { position: relative; z-index: 1; }
        .header h1 { font-size: 2.2em; margin-bottom: 8px; font-weight: 700; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        
        .nav-tabs {
            background: #f8f9fa;
            padding: 0;
            display: flex;
            border-bottom: 1px solid #e9ecef;
        }
        .nav-tab {
            padding: 15px 25px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1em;
            font-weight: 500;
            color: #6c757d;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .nav-tab:hover, .nav-tab.active {
            color: #007bff;
            border-bottom-color: #007bff;
            background: white;
        }
        
        .tab-content { display: none; padding: 30px; }
        .tab-content.active { display: block; }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; }
        .card { 
            background: #ffffff; 
            border-radius: 15px; 
            padding: 25px; 
            border: 1px solid #e9ecef;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(0,0,0,0.1); 
        }
        .card h3 { color: #333; margin-bottom: 20px; font-size: 1.4em; font-weight: 600; }
        
        .status-indicator { 
            display: inline-flex;
            align-items: center;
            padding: 8px 15px; 
            border-radius: 25px; 
            font-weight: 600; 
            margin: 5px 0;
            font-size: 0.9em;
        }
        .status-indicator::before {
            content: '';
            width: 8px; height: 8px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        .running { background: #d4edda; color: #155724; }
        .running::before { background: #28a745; }
        .paused { background: #fff3cd; color: #856404; }
        .paused::before { background: #ffc107; }
        .stopped { background: #f8d7da; color: #721c24; }
        .stopped::before { background: #dc3545; animation: none; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .btn { 
            padding: 12px 20px; 
            border: none; 
            border-radius: 10px; 
            cursor: pointer; 
            font-size: 0.95em; 
            font-weight: 500;
            margin: 5px 5px 5px 0; 
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        .btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .btn:active { transform: translateY(0); }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: #212529; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-outline { background: white; border: 2px solid #007bff; color: #007bff; }
        
        .task-item { 
            background: #f8f9fa; 
            margin: 12px 0; 
            padding: 20px; 
            border-radius: 12px; 
            border-left: 5px solid #28a745;
            transition: all 0.3s;
            position: relative;
        }
        .task-item:hover { background: #e9ecef; }
        .task-item .task-id { 
            position: absolute; 
            top: 10px; right: 15px; 
            background: #007bff; 
            color: white; 
            padding: 4px 8px; 
            border-radius: 15px; 
            font-size: 0.8em; 
            font-weight: 600;
        }
        .task-item.pending-approval { border-left-color: #ffc107; background: #fff3cd; }
        .task-item.completed { border-left-color: #28a745; opacity: 0.8; }
        
        .logs-container { 
            max-height: 300px; 
            overflow-y: auto; 
            background: #1a1a1a; 
            color: #e0e0e0; 
            padding: 20px; 
            border-radius: 12px; 
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 0.9em;
            line-height: 1.6;
        }
        .log-entry { 
            margin: 3px 0; 
            padding: 2px 0;
            border-left: 3px solid transparent;
            padding-left: 10px;
        }
        .log-entry.info { border-left-color: #007bff; }
        .log-entry.success { border-left-color: #28a745; }
        .log-entry.warning { border-left-color: #ffc107; }
        .log-entry.error { border-left-color: #dc3545; }
        
        .form-group { margin: 15px 0; }
        .form-control { 
            width: 100%; 
            padding: 15px; 
            border: 2px solid #e9ecef; 
            border-radius: 10px; 
            font-size: 1em;
            transition: border-color 0.3s;
        }
        .form-control:focus { 
            outline: none; 
            border-color: #007bff; 
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }
        
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); 
            gap: 15px; 
            margin: 20px 0; 
        }
        .stat-card { 
            text-align: center; 
            padding: 20px 15px; 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
            border-radius: 15px;
            transition: transform 0.3s;
        }
        .stat-card:hover { transform: scale(1.05); }
        .stat-value { font-size: 2.2em; font-weight: 700; margin-bottom: 5px; }
        .stat-label { font-size: 0.9em; opacity: 0.9; font-weight: 500; }
        
        .approval-panel {
            background: linear-gradient(135deg, #fff3cd, #ffeaa7);
            border: 2px solid #ffc107;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            text-align: center;
        }
        .approval-panel h4 { color: #856404; margin-bottom: 15px; font-size: 1.3em; }
        
        .progress-bar {
            background: #e9ecef;
            border-radius: 10px;
            height: 8px;
            margin: 10px 0;
            overflow: hidden;
        }
        .progress-fill {
            background: linear-gradient(90deg, #28a745, #20c997);
            height: 100%;
            transition: width 1s ease;
            border-radius: 10px;
        }
        
        .session-item {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            border-left: 5px solid #007bff;
            cursor: pointer;
            transition: all 0.3s;
        }
        .session-item:hover { background: #e9ecef; transform: translateX(5px); }
        
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        .modal.active { display: flex; }
        .modal-content {
            background: white;
            border-radius: 20px;
            padding: 30px;
            max-width: 80%;
            max-height: 80%;
            overflow-y: auto;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        
        .scrollable { max-height: 400px; overflow-y: auto; }
        
        @media (max-width: 768px) {
            .container { margin: 10px; border-radius: 15px; }
            .grid { grid-template-columns: 1fr; }
            .nav-tabs { flex-wrap: wrap; }
            .nav-tab { flex: 1; min-width: 120px; }
        }
    </style>
    <script>
        let currentData = {};
        
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
        }
        
        function updateDashboard() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    currentData = data;
                    updateMainDashboard(data);
                    updateApprovalPanel(data);
                    updateHistoryPanel(data);
                })
                .catch(error => console.error('Update failed:', error));
        }
        
        function updateMainDashboard(data) {
            // Status and basic info
            const statusEl = document.getElementById('status');
            statusEl.textContent = data.status;
            statusEl.className = 'status-indicator ' + data.status.toLowerCase();
            
            document.getElementById('objective').textContent = data.objective;
            document.getElementById('iteration').textContent = data.iteration;
            document.getElementById('tasks-count').textContent = data.tasks_count;
            document.getElementById('completed-count').textContent = data.stats.total_tasks_completed;
            document.getElementById('success-rate').textContent = data.stats.success_rate + '%';
            
            // Progress bar
            const progress = Math.min((data.iteration / data.max_iterations) * 100, 100);
            document.getElementById('progress-fill').style.width = progress + '%';
            
            // Task list
            const taskList = document.getElementById('task-list');
            taskList.innerHTML = '';
            data.tasks.forEach(task => {
                const div = document.createElement('div');
                div.className = 'task-item';
                div.innerHTML = `
                    <div class="task-id">#${task.task_id}</div>
                    <strong>Task:</strong> ${task.task_name}
                    <div style="margin-top: 10px;">
                        <button class="btn btn-outline" onclick="editTask('${task.task_id}')">Edit</button>
                        <button class="btn btn-danger" onclick="removeTask('${task.task_id}')">Remove</button>
                    </div>
                `;
                taskList.appendChild(div);
            });
            
            // Logs
            const logs = document.getElementById('logs');
            logs.innerHTML = '';
            data.logs.slice(-30).forEach(log => {
                const div = document.createElement('div');
                div.className = 'log-entry ' + log.level;
                div.innerHTML = `[${log.timestamp}] ${log.message}`;
                logs.appendChild(div);
            });
            logs.scrollTop = logs.scrollHeight;
        }
        
        function updateApprovalPanel(data) {
            const approvalPanel = document.getElementById('approval-panel');
            if (data.pending_approval) {
                approvalPanel.style.display = 'block';
                document.getElementById('pending-task').innerHTML = `
                    <strong>Task #${data.pending_approval.task_id}:</strong><br>
                    ${data.pending_approval.task_name}
                `;
            } else {
                approvalPanel.style.display = 'none';
            }
        }
        
        function updateHistoryPanel(data) {
            const historyList = document.getElementById('history-list');
            historyList.innerHTML = '';
            data.session_history.forEach((session, index) => {
                const div = document.createElement('div');
                div.className = 'session-item';
                const startTime = new Date(session.start_time).toLocaleString();
                const duration = session.end_time ? 
                    Math.round((new Date(session.end_time) - new Date(session.start_time)) / 60000) + ' min' : 
                    'In Progress';
                
                div.innerHTML = `
                    <strong>Session ${index + 1}</strong> - ${startTime}<br>
                    <small>Objective: ${session.objective.substring(0, 50)}...</small><br>
                    <small>Tasks: ${session.completed_tasks.length} completed, Duration: ${duration}</small>
                `;
                div.onclick = () => showSessionDetails(session);
                historyList.appendChild(div);
            });
        }
        
        function sendCommand(command, data = {}) {
            fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: command, ...data})
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
        
        function addCustomTask() {
            const task = document.getElementById('custom-task').value;
            if (task) {
                sendCommand('add_task', {task: task});
                document.getElementById('custom-task').value = '';
            }
        }
        
        function approveTask(approved) {
            sendCommand('approve_task', {approved: approved});
        }
        
        function editTask(taskId) {
            const newDescription = prompt('Enter new task description:');
            if (newDescription) {
                sendCommand('edit_task', {task_id: taskId, description: newDescription});
            }
        }
        
        function removeTask(taskId) {
            if (confirm('Remove this task?')) {
                sendCommand('remove_task', {task_id: taskId});
            }
        }
        
        function showSessionDetails(session) {
            const modal = document.getElementById('session-modal');
            const content = document.getElementById('session-details');
            content.innerHTML = `
                <h3>Session Details</h3>
                <p><strong>Objective:</strong> ${session.objective}</p>
                <p><strong>Duration:</strong> ${new Date(session.start_time).toLocaleString()} - ${session.end_time ? new Date(session.end_time).toLocaleString() : 'In Progress'}</p>
                <p><strong>Iterations:</strong> ${session.iterations}</p>
                <p><strong>Completed Tasks:</strong> ${session.completed_tasks.length}</p>
                <h4>Completed Tasks:</h4>
                <div class="scrollable">
                    ${session.completed_tasks.map(task => `
                        <div class="task-item completed">
                            <div class="task-id">#${task.task_id}</div>
                            <strong>${task.task_name}</strong><br>
                            <small>Completed: ${new Date(task.completed_at).toLocaleString()}</small>
                        </div>
                    `).join('')}
                </div>
            `;
            modal.classList.add('active');
        }
        
        function closeModal() {
            document.getElementById('session-modal').classList.remove('active');
        }
        
        // Auto-refresh every 2 seconds
        setInterval(updateDashboard, 2000);
        
        // Initial load
        window.onload = () => {
            showTab('dashboard');
            updateDashboard();
        };
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>🤖 Autonomous Task Agent</h1>
                <p>Enhanced Dashboard with Real-time Control & History</p>
            </div>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('dashboard')">📊 Dashboard</button>
            <button class="nav-tab" onclick="showTab('approval')">✅ Task Approval</button>
            <button class="nav-tab" onclick="showTab('history')">📚 Session History</button>
            <button class="nav-tab" onclick="showTab('controls')">⚙️ Controls</button>
        </div>
        
        <!-- Main Dashboard Tab -->
        <div id="dashboard" class="tab-content active">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value" id="iteration">0</div>
                    <div class="stat-label">Iterations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="tasks-count">0</div>
                    <div class="stat-label">Queue</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="completed-count">0</div>
                    <div class="stat-label">Completed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="success-rate">100</div>
                    <div class="stat-label">Success %</div>
                </div>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>🎯 Agent Status</h3>
                    <div id="status" class="status-indicator stopped">Stopped</div>
                    
                    <div style="margin: 20px 0;">
                        <strong>Current Objective:</strong>
                        <p id="objective" style="margin: 10px 0; padding: 15px; background: #f8f9fa; border-radius: 8px;">Loading...</p>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <strong>Progress:</strong>
                        <div class="progress-bar">
                            <div id="progress-fill" class="progress-fill" style="width: 0%"></div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <button class="btn btn-success" onclick="sendCommand('start')">▶️ Start Agent</button>
                        <button class="btn btn-warning" onclick="sendCommand('pause')">⏸️ Pause</button>
                        <button class="btn btn-danger" onclick="sendCommand('stop')">⏹️ Stop</button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📋 Task Queue</h3>
                    <div id="task-list" class="scrollable">
                        Loading tasks...
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h3>📜 Live Activity Logs</h3>
                <div id="logs" class="logs-container">
                    Loading logs...
                </div>
            </div>
        </div>
        
        <!-- Task Approval Tab -->
        <div id="approval" class="tab-content">
            <div id="approval-panel" class="approval-panel" style="display: none;">
                <h4>⏳ Task Awaiting Approval</h4>
                <div id="pending-task" style="margin: 20px 0; padding: 15px; background: white; border-radius: 10px;">
                    No pending tasks
                </div>
                <button class="btn btn-success" onclick="approveTask(true)">✅ Approve & Execute</button>
                <button class="btn btn-danger" onclick="approveTask(false)">❌ Reject Task</button>
            </div>
            
            <div class="card">
                <h3>🎚️ Approval Settings</h3>
                <div class="form-group">
                    <label><input type="checkbox" id="require-approval" checked> Require approval for all tasks</label>
                </div>
                <div class="form-group">
                    <label><input type="checkbox" id="auto-approve-similar"> Auto-approve similar tasks</label>
                </div>
                <button class="btn btn-primary" onclick="sendCommand('update_settings')">Save Settings</button>
            </div>
        </div>
        
        <!-- Session History Tab -->
        <div id="history" class="tab-content">
            <div class="card">
                <h3>📚 Previous Sessions</h3>
                <div id="history-list" class="scrollable">
                    Loading session history...
                </div>
            </div>
        </div>
        
        <!-- Controls Tab -->
        <div id="controls" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h3>🎯 Update Objective</h3>
                    <div class="form-group">
                        <input type="text" id="new-objective" class="form-control" placeholder="Enter new objective...">
                        <button class="btn btn-primary" onclick="updateObjective()">Update Objective</button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>➕ Add Custom Task</h3>
                    <div class="form-group">
                        <input type="text" id="custom-task" class="form-control" placeholder="Enter task description...">
                        <button class="btn btn-success" onclick="addCustomTask()">Add Task</button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🔧 Agent Controls</h3>
                    <button class="btn btn-warning" onclick="sendCommand('clear_tasks')">🗑️ Clear All Tasks</button>
                    <button class="btn btn-secondary" onclick="sendCommand('reset_stats')">📊 Reset Statistics</button>
                    <button class="btn btn-primary" onclick="sendCommand('save_session')">💾 Save Session</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Session Details Modal -->
    <div id="session-modal" class="modal">
        <div class="modal-content">
            <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 20px;">
                <h2 style="flex: 1;">Session Details</h2>
                <button class="btn btn-secondary" onclick="closeModal()">✕ Close</button>
            </div>
            <div id="session-details"></div>
        </div>
    </div>
</body>
</html>
"""

# Enhanced API endpoints
@app.route('/')
def dashboard():
    return ENHANCED_DASHBOARD_HTML

@app.route('/api/status')
def api_status():
    status = "Running" if agent_state.is_running else ("Paused" if agent_state.is_paused else "Stopped")
    return jsonify({
        'status': status,
        'objective': agent_state.objective,
        'iteration': agent_state.iteration,
        'max_iterations': agent_state.max_iterations,
        'tasks_count': len(agent_state.task_list),
        'tasks': [{'task_id': t['task_id'], 'task_name': t['task_name']} for t in list(agent_state.task_list)],
        'completed_tasks': agent_state.completed_tasks,
        'pending_approval': agent_state.pending_approval,
        'approval_required': agent_state.approval_required,
        'session_history': agent_state.session_history,
        'stats': agent_state.execution_stats,
        'logs': agent_state.logs[-50:]  # Last 50 logs
    })

@app.route('/api/command', methods=['POST'])
def api_command():
    command = request.json.get('command')
    data = request.json
    
    if command == 'start':
        if not agent_state.is_running:
            agent_state.is_running = True
            agent_state.is_paused = False
            agent_state.start_time = datetime.datetime.now().isoformat()
            agent_state.add_log("🚀 Agent started", "success")
            threading.Thread(target=run_enhanced_agent_background, daemon=True).start()
    
    elif command == 'pause':
        agent_state.is_paused = not agent_state.is_paused
        status = "paused" if agent_state.is_paused else "resumed"
        agent_state.add_log(f"⏸️ Agent {status}", "warning")
    
    elif command == 'stop':
        agent_state.is_running = False
        agent_state.is_paused = False
        agent_state.save_session()
        agent_state.add_log("⏹️ Agent stopped", "error")
    
    elif command == 'approve_task':
        approved = data.get('approved', False)
        if agent_state.pending_approval:
            if approved:
                agent_state.add_log(f"✅ Task approved: {agent_state.pending_approval['task_name'][:30]}...", "success")
            else:
                agent_state.add_log(f"❌ Task rejected: {agent_state.pending_approval['task_name'][:30]}...", "warning")
            agent_state.pending_approval['approved'] = approved
    
    elif command == 'add_task':
        task_desc = data.get('task')
        if task_desc:
            agent_state.task_id_counter += 1
            new_task = {"task_id": agent_state.task_id_counter, "task_name": task_desc}
            agent_state.task_list.append(new_task)
            agent_state.add_log(f"➕ Custom task added: {task_desc[:30]}...", "info")
    
    elif command == 'edit_task':
        task_id = int(data.get('task_id'))
        new_desc = data.get('description')
        for task in agent_state.task_list:
            if task['task_id'] == task_id:
                old_desc = task['task_name']
                task['task_name'] = new_desc
                agent_state.add_log(f"✏️ Task edited: #{task_id}", "info")
                break
    
    elif command == 'remove_task':
        task_id = int(data.get('task_id'))
        original_length = len(agent_state.task_list)
        agent_state.task_list = deque([t for t in agent_state.task_list if t['task_id'] != task_id])
        if len(agent_state.task_list) < original_length:
            agent_state.add_log(f"🗑️ Task removed: #{task_id}", "warning")
    
    elif command == 'clear_tasks':
        agent_state.task_list.clear()
        agent_state.add_log("🗑️ All tasks cleared", "warning")
    
    elif command == 'reset_stats':
        agent_state.execution_stats = {
            'total_tasks_completed': 0,
            'total_tasks_generated': 0,
            'success_rate': 100,
            'avg_execution_time': 0
        }
        agent_state.add_log("📊 Statistics reset", "info")
    
    elif command == 'save_session':
        agent_state.save_session()
        agent_state.add_log("💾 Session saved to history", "success")
    
    return jsonify({'success': True})

@app.route('/api/objective', methods=['POST'])
def api_objective():
    new_objective = request.json.get('objective')
    if new_objective:
        old_objective = agent_state.objective
        agent_state.objective = new_objective
        agent_state.add_log(f"🎯 Objective updated: {new_objective[:50]}...", "info")
    return jsonify({'success': True})

def run_enhanced_agent_background():
    """Enhanced background agent with approval workflow."""
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
        
        # Get next task
        task = agent_state.task_list.popleft()
        agent_state.current_task = task
        
        # Handle approval workflow
        if agent_state.approval_required:
            agent_state.pending_approval = task.copy()
            agent_state.add_log(f"⏳ Task pending approval: {task['task_name'][:50]}...", "warning")
            
            # Wait for approval
            timeout = 0
            while agent_state.is_running and 'approved' not in agent_state.pending_approval:
                time.sleep(1)
                timeout += 1
                if timeout > 300:  # 5 minute timeout
                    agent_state.add_log("⏰ Approval timeout - auto-approving task", "warning")
                    agent_state.pending_approval['approved'] = True
                    break
            
            if not agent_state.pending_approval.get('approved', False):
                agent_state.add_log(f"⏭️ Task skipped: {task['task_name'][:30]}...", "warning")
                agent_state.pending_approval = None
                continue
            
            agent_state.pending_approval = None
        
        # Execute task
        agent_state.add_log(f"⚡ Executing: {task['task_name'][:50]}...", "info")
        
        try:
            start_time = time.time()
            result = execution_agent(agent_state.objective, task["task_name"])
            execution_time = time.time() - start_time
            
            agent_state.last_result = result
            
            # Update statistics
            agent_state.execution_stats['total_tasks_completed'] += 1
            agent_state.execution_stats['avg_execution_time'] = (
                (agent_state.execution_stats['avg_execution_time'] * (agent_state.execution_stats['total_tasks_completed'] - 1) + execution_time) /
                agent_state.execution_stats['total_tasks_completed']
            )
            
            # Store completed task
            completed_task = {
                'task_id': task['task_id'],
                'task_name': task['task_name'],
                'result': result[:200] + '...' if len(result) > 200 else result,
                'completed_at': datetime.datetime.now().isoformat(),
                'execution_time': execution_time
            }
            agent_state.completed_tasks.append(completed_task)
            
            agent_state.add_log(f"✅ Task completed: {task['task_name'][:30]}...", "success")
            
            # Store result in database
            embedding = get_mistral_embedding(result)
            store_task_result(str(task['task_id']), task["task_name"], result, embedding)
            
            # Generate new tasks
            new_tasks = task_creation_agent(
                agent_state.objective,
                {"data": result},
                task["task_name"],
                [t["task_name"] for t in agent_state.task_list]
            )
            
            # Add new tasks (limit to 2 to prevent explosion)
            for new_task in new_tasks[:2]:
                agent_state.task_id_counter += 1
                new_task.update({"task_id": agent_state.task_id_counter})
                agent_state.task_list.append(new_task)
                agent_state.execution_stats['total_tasks_generated'] += 1
            
            if new_tasks:
                agent_state.add_log(f"💡 Generated {len(new_tasks[:2])} new tasks", "info")
            
            # Prioritize tasks
            if len(agent_state.task_list) > 1:
                prioritization_agent(int(task["task_id"]), agent_state.task_list, agent_state.objective)
                agent_state.add_log("📋 Tasks reprioritized", "info")
            
            agent_state.iteration += 1
            time.sleep(2)  # Brief pause between tasks
            
        except Exception as e:
            agent_state.add_log(f"❌ Error executing task: {str(e)[:50]}...", "error")
            agent_state.execution_stats['success_rate'] = max(0, agent_state.execution_stats['success_rate'] - 5)
            time.sleep(5)
    
    agent_state.is_running = False
    agent_state.save_session()
    agent_state.add_log("🏁 Agent execution completed", "success")

if __name__ == '__main__':
    print("🌐 Starting Enhanced Autonomous Task Agent Web Dashboard...")
    print("📱 Features: Real-time interface, task approval, session history")
    print("🔗 Open your browser to: http://localhost:5000")
    print("🔧 Use Ctrl+C to stop the server")
    
    # Initialize with first task
    first_task = {"task_id": 1, "task_name": YOUR_FIRST_TASK}
    agent_state.task_list.append(first_task)
    agent_state.add_log("🤖 Enhanced dashboard initialized", "info")
    
    app.run(debug=False, host='0.0.0.0', port=5000)