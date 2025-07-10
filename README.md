# 🤖 Autonomous Task Agent

A Python-based autonomous task management system that generates, prioritizes, and executes tasks toward a specified objective using Mistral AI for text generation and embeddings, and Supabase (PostgreSQL) with `pgvector` for vector storage.

## ✨ Features

- 🎯 **Objective-Driven**: Generates tasks based on a specified objective (e.g., "Solve world hunger")
- 🧠 **AI-Powered**: Uses Mistral's latest models for task creation, prioritization, and execution
- 📊 **Vector Storage**: Stores task results as embeddings in Supabase for semantic search
- 🔄 **Adaptive**: Continuously generates new tasks based on previous results
- 🚀 **Cloud-Ready**: Deployable on Render with Docker and managed PostgreSQL
- 🛡️ **Error Handling**: Robust error handling and fallback mechanisms

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Task Creation  │    │ Prioritization  │    │   Execution     │
│     Agent       │───▶│     Agent       │───▶│     Agent       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                                              │
         │              ┌─────────────────┐             │
         └──────────────│  Context Agent  │◀────────────┘
                        │ (Vector Search) │
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │ Supabase + pgvector │
                        │   Vector Store  │
                        └─────────────────┘
```

## 📋 Prerequisites

- Python 3.11+
- Mistral API key (from `api.mistral.ai`)
- Supabase account (from `supabase.com`)
- Docker (optional, for containerization)

## 🎮 How to Interact with the Agent

The agent offers **multiple interaction modes** to suit different preferences:

### 1. **Autonomous Mode** (Default) 🤖
**Best for:** Set-and-forget operation, testing, production runs

```bash
python -m src.main
```

- Agent runs completely autonomously
- You set the objective and watch it execute
- Minimal user interaction required
- Ideal for long-running tasks

### 2. **Interactive CLI Mode** 💬
**Best for:** Hands-on control, learning, experimentation

```bash
python interactive_agent.py
```

**Features:**
- ⏸️ Pause/resume execution at any time
- ✅ Approve or reject each task before execution
- ✏️ Edit task descriptions in real-time
- 🎯 Change objectives during execution
- ➕ Add custom tasks manually
- 📋 View and manage task queue
- 📊 Real-time statistics and progress

### 3. **Web Dashboard** 🌐
**Best for:** Visual monitoring, team collaboration, remote access

```bash
python web_dashboard.py
# Open browser to http://localhost:5000
```

**Features:**
- 📱 Beautiful web interface accessible from any device
- 🔄 Real-time updates without page refresh
- 📈 Visual progress tracking and statistics
- 🎛️ Point-and-click controls (start/stop/pause)
- 📝 Live task queue management
- 📜 Activity logs with timestamps
- 🎯 Update objectives through web form

### 4. **Test Mode** 🧪
**Best for:** Validation, debugging, quick tests

```bash
python test_agent.py
```

**Features:**
- 🔍 Validates configuration and API connections
- 🏃 Mini demo with limited iterations
- 📊 Component-by-component testing
- 🛠️ Troubleshooting guidance

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/autonomous-task-agent.git
cd autonomous-task-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
MISTRAL_API_KEY=your_mistral_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
OBJECTIVE=Solve world hunger.
YOUR_TABLE_NAME=documents
YOUR_FIRST_TASK=Develop a task list.
```

### 4. Setup Supabase Database

#### Option A: Automatic Setup (Recommended)
The application will automatically create the required table and functions when you run it.

#### Option B: Manual Setup
If you prefer manual setup or encounter issues, run the SQL commands in `setup_supabase.txt` in your Supabase SQL editor.

### 5. Run the Agent

```bash
python -m src.main
```

## 🐳 Docker Deployment

### Build and Run Locally

```bash
# Build the image
docker build -t autonomous-task-agent .

# Run the container
docker run --env-file .env autonomous-task-agent
```

### Deploy to Render

1. **Fork this repository** to your GitHub account

2. **Create a new Web Service** on Render:
   - Connect your GitHub repository
   - Set the build command: `pip install -r requirements.txt`
   - Set the start command: `python -m src.main`

3. **Add Environment Variables** in Render dashboard:
   - `MISTRAL_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `OBJECTIVE`
   - `YOUR_TABLE_NAME`
   - `YOUR_FIRST_TASK`

4. **Deploy** and monitor the logs

## 📁 Project Structure

```
autonomous-task-agent/
├── src/
│   ├── __init__.py
│   ├── main.py          # Main execution loop
│   ├── agents.py        # AI agents for task management
│   ├── database.py      # Supabase database operations
│   └── config.py        # Configuration and environment setup
├── .env.example         # Environment variables template
├── .env                 # Your environment variables (not in git)
├── Dockerfile           # Container configuration
├── requirements.txt     # Python dependencies
├── setup_supabase.txt   # Database setup SQL
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MISTRAL_API_KEY` | Your Mistral AI API key | Required |
| `SUPABASE_URL` | Your Supabase project URL | Required |
| `SUPABASE_ANON_KEY` | Your Supabase anonymous key | Required |
| `OBJECTIVE` | The main objective for the agent | "Solve world hunger." |
| `YOUR_TABLE_NAME` | Database table name | "documents" |
| `YOUR_FIRST_TASK` | Initial task to start with | "Develop a task list." |

### Agent Configuration

You can modify the following parameters in `src/main.py`:

- `max_iterations`: Maximum number of task cycles (default: 10)
- Model selection in `src/agents.py` (currently using `mistral-large-latest`)

## 🧪 How It Works

1. **Initialization**: Sets up database and loads the first task
2. **Task Execution**: AI agent executes the current task
3. **Result Storage**: Task results are embedded and stored in Supabase
4. **Task Generation**: New tasks are created based on the objective and results
5. **Prioritization**: Tasks are reordered by importance and relevance
6. **Context Retrieval**: Previous results provide context for future tasks
7. **Repeat**: Process continues until completion or max iterations

## 🔍 Example Output

```
*****OBJECTIVE*****
Solve world hunger.

🚀 Starting autonomous task agent with objective: Solve world hunger.

*****TASK LIST*****
1: Develop a task list.

*****NEXT TASK*****
1: Develop a task list.

⚡ Executing task...

*****TASK RESULT*****
Based on the objective to solve world hunger, here is a comprehensive task list:

1. Research current global hunger statistics and affected regions
2. Analyze root causes of food insecurity worldwide
3. Investigate successful hunger reduction programs
4. Identify key stakeholders and organizations
...
```

## 🛠️ Troubleshooting

### Common Issues

1. **Mistral API Errors**
   - Verify your API key is correct
   - Check your API usage limits
   - Ensure you have access to the required models

2. **Supabase Connection Issues**
   - Verify your Supabase URL and keys
   - Check if pgvector extension is enabled
   - Ensure proper database permissions

3. **Vector Search Errors**
   - The system will fall back to basic table creation if vector extensions aren't available
   - Check Supabase logs for detailed error messages

### Database Setup Issues

If automatic table creation fails, manually run the SQL in `setup_supabase.txt`:

1. Go to your Supabase dashboard
2. Navigate to SQL Editor
3. Copy and paste the SQL commands
4. Execute them one by one

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Mistral AI](https://mistral.ai/) for powerful language models
- [Supabase](https://supabase.com/) for managed PostgreSQL with vector support
- [pgvector](https://github.com/pgvector/pgvector) for vector similarity search

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/autonomous-task-agent/issues) page
2. Create a new issue with detailed information
3. Include error logs and environment details

---

**Happy Task Automating! 🚀**