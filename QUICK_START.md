# 🎮 Agent Interaction Summary

## TL;DR - How to Use Your Agent

You have **4 different ways** to interact with your autonomous task agent:

### 🟢 **Quick Start (Recommended for beginners)**
```bash
make install    # Install dependencies
make test       # Validate setup  
make demo       # Interactive mode selector
```

### 🟡 **Direct Commands**
```bash
make run         # Autonomous mode (set and forget)
make interactive # Interactive CLI (full control)
make web         # Web dashboard (visual interface)
```

---

## 🎯 Which Mode Should I Use?

### **I want to set an objective and let it run** → `make run`
- Perfect for: Testing, production, hands-off operation
- You set the goal, agent executes autonomously
- Minimal interaction required

### **I want full control over each step** → `make interactive`  
- Perfect for: Learning, experimentation, careful oversight
- Approve/reject/edit every task
- Pause, resume, change objectives anytime

### **I want a visual interface** → `make web`
- Perfect for: Monitoring, team collaboration, mobile access
- Beautiful web dashboard at http://localhost:5000
- Point-and-click controls, real-time updates

### **I want to explore all options** → `make demo`
- Perfect for: First-time users, comparing modes
- Interactive guide to all interaction methods
- Try before you commit

---

## 🚀 30-Second Setup

1. **Get your API keys:**
   - Mistral API: https://api.mistral.ai
   - Supabase: https://supabase.com

2. **Configure:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install & Test:**
   ```bash
   make install
   make test
   ```

4. **Choose your interaction style:**
   ```bash
   make demo    # Explore all options
   # OR
   make run     # Go autonomous
   # OR  
   make interactive  # Take control
   # OR
   make web     # Visual dashboard
   ```

---

## 📱 Real-World Usage Examples

### **Example 1: Learning Mode**
```bash
# Set objective: "Learn advanced Python web development"
make interactive
# Approve each learning task, add custom practice projects
```

### **Example 2: Business Mode**  
```bash
# Set objective: "Create a comprehensive marketing strategy"
make web
# Monitor progress from phone/laptop, collaborate with team
```

### **Example 3: Research Mode**
```bash
# Set objective: "Research renewable energy trends for 2024"
make run
# Let it run autonomously, review final research compilation
```

### **Example 4: Development Mode**
```bash
# Set objective: "Build a SaaS product roadmap"
make interactive
# Guide each step, add domain expertise, iterate on results
```

---

## 🛠️ Advanced Configuration

### **Customize Your Objective**
Edit `.env` file:
```env
OBJECTIVE=Your specific goal here
YOUR_FIRST_TASK=Where to start
```

### **Control Execution**
- **Max iterations**: Edit `max_iterations` in source code
- **Task limits**: Modify task generation limits
- **API models**: Switch Mistral models in `agents.py`

### **Database Management**
- **View data**: Access Supabase dashboard
- **Export results**: Download task results and embeddings
- **Cleanup**: Optional table deletion after execution

---

## 🔧 Troubleshooting

### **"Configuration test failed"**
- Check your `.env` file has correct API keys
- Verify Supabase URL and keys are valid

### **"API connection failed"**
- Confirm Mistral API key has sufficient credits
- Test Supabase connection in their dashboard

### **"No tasks generated"**
- Try a more specific objective
- Check if max iterations was reached
- Review task creation prompts

### **"Dependencies missing"**
```bash
make clean
make install
```

---

## 🎉 You're Ready!

Your autonomous task agent is now fully configured with multiple interaction modes. Whether you prefer hands-off automation or hands-on control, there's an interface that fits your workflow.

**🚀 Start with:** `make demo` to explore all options  
**⚡ Quick run:** `make test && make run`  
**🎯 Full control:** `make interactive`  
**📱 Visual mode:** `make web`

**Happy automating! 🤖✨**