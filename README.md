# 🚀 CareerPilot AI

### AI-Powered Career Guidance & Assistance Platform

**CareerPilot AI** is an AI-powered career guidance platform designed to help students and job seekers explore career opportunities, understand their skills, receive personalized guidance, and interact with an intelligent career assistant.

The project combines a web-based interface, Python backend services, a structured knowledge layer, database support, and local AI capabilities to create an interactive career assistance system.

---

## ✨ Key Features

### 🤖 AI Career Assistant

Interact with an AI-powered assistant to ask questions related to:

* Career options
* Skills and technologies
* Job roles
* Learning paths
* Professional development
* Career planning

### 🎯 Career Guidance

CareerPilot AI is designed to help users understand potential career directions based on their interests, skills, and goals.

### 🧠 Knowledge-Based Assistance

The application includes a dedicated knowledge layer that can provide structured career-related information to the AI system.

### 🧩 Agent-Based Architecture

The project uses an agent-oriented architecture to organize different areas of career assistance and application logic.

### 💬 Interactive Web Interface

A browser-based interface allows users to interact with the CareerPilot AI system through a clean and responsive frontend.

### 🗄️ Database Integration

SQLite is used for local application data storage and management.

### 🔐 Security

The project includes application-level security functionality for handling application data and user interactions.

### 🧠 Local AI Support

CareerPilot AI includes integration with **Ollama** for working with locally hosted language models.

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │       User          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Web Interface    │
                         │   HTML / CSS / JS   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Flask Backend    │
                         │       app.py        │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │ Orchestrator │ │    Agents    │ │   Services   │
            └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
                   │                │                │
                   └────────────────┼────────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │  Knowledge Layer    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Ollama / LLM      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   SQLite Database   │
                         └─────────────────────┘
```

---

#
