from agents.agents import CareerAgent,SkillAgent,LearningAgent,ResumeAgent,PlacementAgent,InterviewAgent,ProjectAgent
from db import get_db

class Orchestrator:
    def __init__(self,uid):
        self.uid=uid
        self.agents=[CareerAgent(),SkillAgent(),LearningAgent(),ResumeAgent(),PlacementAgent(),InterviewAgent(),ProjectAgent()]
    def log(self,a,action,status='completed',details=''):
        with get_db() as c:c.execute('INSERT INTO activities(user_id,agent,action,status,details) VALUES(?,?,?,?,?)',(self.uid,a,action,status,details))
    def analyze(self,p):
        c={'profile':p};o={}
        for a in self.agents:
            try:
                key=a.name.lower().replace(' ','_')
                if a.name=='Skill Agent':o['skills']=a.run(c);c['skills']=o['skills']
                elif a.name=='Learning Agent':o['learning']=a.run(c);c['learning']=o['learning']
                elif a.name=='Resume Agent':o['resume_agent']=a.run(c);c['resume_agent']=o['resume_agent']
                else:o[key]=a.run(c);c[key]=o[key]
                self.log(a.name,'Executed analysis')
            except Exception as e:
                self.log(a.name,'Execution failed','error',str(e));raise
        readiness=o['placement_agent']['readiness']
        o['digital_twin']={'current':p.get('skills',''),'target':p.get('target_role',''),'gaps':o['skills']['gaps'],'readiness':readiness,'next_actions':o['learning']['weekly_focus']}
        o['summary']=f"Target: {p.get('target_role') or 'Software Developer'}. Skill coverage is {o['skills']['coverage']}%, portfolio health is {o['resume_agent']['health']}%, and placement readiness is {readiness}%. Priority gaps: {', '.join(o['skills']['gaps'][:4]) or 'None'}."
        o['explainability']=[
          {'factor':'Skill coverage','value':o['skills']['coverage'],'reason':'Measures matched target-role skills.'},
          {'factor':'Portfolio health','value':o['resume_agent']['health'],'reason':'Checks evidence, projects, certifications and resume signals.'},
          {'factor':'Placement readiness','value':readiness,'reason':'Combines skill coverage, portfolio evidence and experience level.'}]
        return o
