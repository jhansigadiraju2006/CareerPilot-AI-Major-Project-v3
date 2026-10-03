# CareerPilot AI — Advanced Major Project v3

An autonomous, local-first, multi-agent career and placement intelligence platform built with Flask + SQLite.

## Major-project features
- 7-agent career intelligence pipeline
- Career Digital Twin
- Dynamic role-specific Skill Graph
- Adaptive learning roadmap
- Explainable placement readiness
- Resume/portfolio health and ATS keyword analysis
- Job-description skill matching with history
- Career What-if Simulator
- AI Mock Interview with scoring and history
- Portfolio Project Builder
- Job Application Tracker
- Skill progress history
- Agent activity/audit trail
- Persistent AI assistant conversation history
- Evaluation metrics and printable career report
- User authentication and persistent SQLite storage
- Optional Ollama-ready architecture can be added without changing the UI flow

## Run in VS Code
```powershell
python -m venv venv
venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Demo flow for viva
1. Register and login.
2. Fill Student Profile with target role and skills.
3. Run Career Intelligence.
4. Show the 7-agent activity trail.
5. Explain the Skill Graph and Digital Twin.
6. Run a job description through Job Intelligence.
7. Use Career Simulator to add missing skills.
8. Run Mock Interview and show score/history.
9. Add a portfolio project and job application.
10. Open Evaluation and generate the final report.

## Notes
The project works without external AI APIs. The intelligence pipeline is deterministic and explainable so it can be demonstrated offline. If you want a live LLM layer, connect Ollama locally and replace/extend the agent logic in `agents/agents.py`.
