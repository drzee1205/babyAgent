#!/usr/bin/env python3
"""
Demo version of the Enhanced Web Dashboard.
This version shows the interface without requiring all dependencies.
"""

from flask import Flask, jsonify
import json
import time
import datetime
from collections import deque

app = Flask(__name__)

# Demo data for showcase
demo_data = {
    'status': 'Running',
    'objective': 'Solve world hunger through innovative agricultural solutions',
    'iteration': 3,
    'max_iterations': 10,
    'tasks_count': 4,
    'tasks': [
        {'task_id': 4, 'task_name': 'Research vertical farming technologies and their scalability'},
        {'task_id': 5, 'task_name': 'Analyze distribution networks in food-insecure regions'},
        {'task_id': 6, 'task_name': 'Develop partnerships with agricultural technology companies'},
        {'task_id': 7, 'task_name': 'Create implementation timeline for pilot programs'}
    ],
    'completed_tasks': [
        {
            'task_id': 1,
            'task_name': 'Develop a comprehensive task list',
            'result': 'Created detailed breakdown of hunger-solving initiatives including research, technology, distribution, and implementation phases...',
            'completed_at': '2024-07-10T12:30:00',
            'execution_time': 45.2
        },
        {
            'task_id': 2,
            'task_name': 'Research current global hunger statistics',
            'result': 'Analyzed data from FAO and WFP showing 828 million people facing acute food insecurity. Key regions identified: Sub-Saharan Africa, South Asia...',
            'completed_at': '2024-07-10T12:35:00',
            'execution_time': 38.7
        },
        {
            'task_id': 3,
            'task_name': 'Identify root causes of food insecurity',
            'result': 'Primary causes: climate change (40%), conflict (35%), economic factors (20%), infrastructure (5%). Developed intervention strategies...',
            'completed_at': '2024-07-10T12:42:00',
            'execution_time': 52.1
        }
    ],
    'pending_approval': {
        'task_id': 4,
        'task_name': 'Research vertical farming technologies and their scalability'
    },
    'approval_required': True,
    'session_history': [
        {
            'start_time': '2024-07-10T11:00:00',
            'end_time': '2024-07-10T11:45:00',
            'objective': 'Learn advanced Python web development',
            'iterations': 8,
            'completed_tasks': [
                {'task_id': 1, 'task_name': 'Research FastAPI framework basics', 'completed_at': '2024-07-10T11:15:00'},
                {'task_id': 2, 'task_name': 'Set up development environment', 'completed_at': '2024-07-10T11:30:00'},
                {'task_id': 3, 'task_name': 'Build sample REST API', 'completed_at': '2024-07-10T11:45:00'}
            ]
        },
        {
            'start_time': '2024-07-09T14:20:00',
            'end_time': '2024-07-09T15:10:00',
            'objective': 'Create a comprehensive marketing strategy',
            'iterations': 5,
            'completed_tasks': [
                {'task_id': 1, 'task_name': 'Analyze target market demographics', 'completed_at': '2024-07-09T14:35:00'},
                {'task_id': 2, 'task_name': 'Research competitor strategies', 'completed_at': '2024-07-09T14:50:00'}
            ]
        }
    ],
    'stats': {
        'total_tasks_completed': 3,
        'total_tasks_generated': 7,
        'success_rate': 95,
        'avg_execution_time': 45.3
    },
    'logs': [
        {'timestamp': '12:30:15', 'message': '🚀 Agent started', 'level': 'success'},
        {'timestamp': '12:30:16', 'message': '🔧 Setting up database...', 'level': 'info'},
        {'timestamp': '12:30:18', 'message': '✅ Database setup completed', 'level': 'success'},
        {'timestamp': '12:30:20', 'message': '📝 Added first task: Develop a comprehensive task list', 'level': 'info'},
        {'timestamp': '12:30:22', 'message': '⚡ Executing: Develop a comprehensive task list', 'level': 'info'},
        {'timestamp': '12:31:07', 'message': '✅ Task completed: Develop a comprehensive task list', 'level': 'success'},
        {'timestamp': '12:31:08', 'message': '💡 Generated 3 new tasks', 'level': 'info'},
        {'timestamp': '12:31:10', 'message': '📋 Tasks reprioritized', 'level': 'info'},
        {'timestamp': '12:31:12', 'message': '⚡ Executing: Research current global hunger statistics', 'level': 'info'},
        {'timestamp': '12:31:50', 'message': '✅ Task completed: Research current global hunger statistics', 'level': 'success'},
        {'timestamp': '12:31:52', 'message': '💡 Generated 2 new tasks', 'level': 'info'},
        {'timestamp': '12:31:54', 'message': '⚡ Executing: Identify root causes of food insecurity', 'level': 'info'},
        {'timestamp': '12:32:46', 'message': '✅ Task completed: Identify root causes of food insecurity', 'level': 'success'},
        {'timestamp': '12:32:48', 'message': '⏳ Task pending approval: Research vertical farming technologies...', 'level': 'warning'},
        {'timestamp': '12:32:50', 'message': '⏸️ Agent paused for task approval', 'level': 'warning'}
    ]
}

# Enhanced HTML (same as before)
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
        
        .demo-banner {
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 10px 20px;
            text-align: center;
            font-weight: 600;
        }
        
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
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
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
            const statusEl = document.getElementById('status');
            statusEl.textContent = data.status;
            statusEl.className = 'status-indicator ' + data.status.toLowerCase();
            
            document.getElementById('objective').textContent = data.objective;
            document.getElementById('iteration').textContent = data.iteration;
            document.getElementById('tasks-count').textContent = data.tasks_count;
            document.getElementById('completed-count').textContent = data.stats.total_tasks_completed;
            document.getElementById('success-rate').textContent = data.stats.success_rate + '%';
            
            const progress = Math.min((data.iteration / data.max_iterations) * 100, 100);
            document.getElementById('progress-fill').style.width = progress + '%';
            
            const taskList = document.getElementById('task-list');
            taskList.innerHTML = '';
            data.tasks.forEach(task => {
                const div = document.createElement('div');
                div.className = 'task-item';
                div.innerHTML = `
                    <div class="task-id">#${task.task_id}</div>
                    <strong>Task:</strong> ${task.task_name}
                    <div style="margin-top: 10px;">
                        <button class="btn btn-outline" onclick="alert('Edit functionality - Demo Mode')">Edit</button>
                        <button class="btn btn-danger" onclick="alert('Remove functionality - Demo Mode')">Remove</button>
                    </div>
                `;
                taskList.appendChild(div);
            });
            
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
        
        function demoAlert(feature) {
            alert(`${feature} - This is a demo interface. In the full version, this would execute the actual functionality with your Mistral AI and Supabase configuration.`);
        }
        
        // Auto-refresh every 3 seconds in demo
        setInterval(updateDashboard, 3000);
        
        window.onload = () => {
            showTab('dashboard');
            updateDashboard();
        };
    </script>
</head>
<body>
    <div class="demo-banner">
        🚀 DEMO MODE - Enhanced Web Dashboard Showcase
    </div>
    
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
                        <button class="btn btn-success" onclick="demoAlert('Start Agent')">▶️ Start Agent</button>
                        <button class="btn btn-warning" onclick="demoAlert('Pause Agent')">⏸️ Pause</button>
                        <button class="btn btn-danger" onclick="demoAlert('Stop Agent')">⏹️ Stop</button>
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
                <button class="btn btn-success" onclick="demoAlert('Approve Task')">✅ Approve & Execute</button>
                <button class="btn btn-danger" onclick="demoAlert('Reject Task')">❌ Reject Task</button>
            </div>
            
            <div class="card">
                <h3>🎚️ Approval Settings</h3>
                <div class="form-group">
                    <label><input type="checkbox" id="require-approval" checked> Require approval for all tasks</label>
                </div>
                <div class="form-group">
                    <label><input type="checkbox" id="auto-approve-similar"> Auto-approve similar tasks</label>
                </div>
                <button class="btn btn-primary" onclick="demoAlert('Save Settings')">Save Settings</button>
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
                        <button class="btn btn-primary" onclick="demoAlert('Update Objective')">Update Objective</button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>➕ Add Custom Task</h3>
                    <div class="form-group">
                        <input type="text" id="custom-task" class="form-control" placeholder="Enter task description...">
                        <button class="btn btn-success" onclick="demoAlert('Add Custom Task')">Add Task</button>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🔧 Agent Controls</h3>
                    <button class="btn btn-warning" onclick="demoAlert('Clear All Tasks')">🗑️ Clear All Tasks</button>
                    <button class="btn btn-secondary" onclick="demoAlert('Reset Statistics')">📊 Reset Statistics</button>
                    <button class="btn btn-primary" onclick="demoAlert('Save Session')">💾 Save Session</button>
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

@app.route('/')
def dashboard():
    return ENHANCED_DASHBOARD_HTML

@app.route('/api/status')
def api_status():
    return jsonify(demo_data)

@app.route('/api/command', methods=['POST'])
def api_command():
    # Demo mode - just return success
    return jsonify({'success': True, 'demo': True})

@app.route('/api/objective', methods=['POST'])
def api_objective():
    # Demo mode - just return success
    return jsonify({'success': True, 'demo': True})

if __name__ == '__main__':
    print("🌐 Starting Enhanced Web Dashboard Demo...")
    print("📱 This demo shows all the features you requested:")
    print("   ✅ Real-time web interface")
    print("   ✅ Visual task management") 
    print("   ✅ Objective modification")
    print("   ✅ Progress tracking")
    print("   ✅ Task approval workflow")
    print("   ✅ Historical session review")
    print()
    print("🔗 Open your browser to: http://localhost:5000")
    print("🔧 Use Ctrl+C to stop the demo")
    
    app.run(debug=False, host='0.0.0.0', port=5000)