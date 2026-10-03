from collections import Counter

class CareerAgent:
    name='Career Agent'
    def run(self,c):
        p=c['profile']; role=p.get('target_role') or 'Software Developer'
        level=p.get('experience_level','Beginner')
        directions={'Beginner':'Build fundamentals, one strong project and interview basics.','Intermediate':'Deepen system design, production practices and role-specific projects.','Advanced':'Demonstrate architecture, leadership, optimization and measurable impact.'}
        return {'target':role,'level':level,'direction':directions.get(level,directions['Beginner']),'milestones':['Core skills','Portfolio evidence','Interview readiness','Job applications']}

class SkillAgent:
    name='Skill Agent'
    roles={
      'java full stack developer':['Java','OOP','Collections','SQL','Spring Boot','REST APIs','JPA/Hibernate','Git','Docker','Angular'],
      'java backend developer':['Java','OOP','Collections','SQL','Spring Boot','REST APIs','JPA/Hibernate','Git','Docker'],
      'devops engineer':['Linux','Git','Networking','Docker','CI/CD','Cloud','Kubernetes','Monitoring','Terraform'],
      'data scientist':['Python','SQL','Statistics','Pandas','NumPy','Machine Learning','Visualization','Git','Model Evaluation'],
      'machine learning engineer':['Python','SQL','Statistics','Machine Learning','Deep Learning','APIs','Docker','Git','Model Deployment'],
      'software developer':['Programming','DSA','Git','SQL','Testing','REST APIs','Debugging','OOP','Databases'],
      'frontend developer':['HTML','CSS','JavaScript','React','Git','REST APIs','Testing','Accessibility'],
      'cloud engineer':['Linux','Networking','Cloud','Docker','Kubernetes','Terraform','CI/CD','Security','Monitoring']}
    def run(self,c):
        p=c['profile']; req=self.roles.get(p.get('target_role','').lower(),self.roles['software developer'])
        have={x.strip().lower() for x in p.get('skills','').split(',') if x.strip()}
        gaps=[x for x in req if x.lower() not in have]
        matched=[x for x in req if x.lower() in have]
        cov=round(len(matched)*100/len(req))
        graph=[{'skill':s,'depends_on':req[i-1] if i else None,'status':'matched' if s in matched else 'gap'} for i,s in enumerate(req)]
        return {'required':req,'matched':matched,'gaps':gaps,'coverage':cov,'graph':graph}

class LearningAgent:
    name='Learning Agent'
    def run(self,c):
        gaps=c['skills']['gaps'][:8] or ['System Design','Testing','Project polishing']
        tasks=[]
        for i,s in enumerate(gaps):
            tasks.append({'day':i+1,'skill':s,'task':f'Study {s}, complete a practical exercise, and record evidence in your portfolio.','priority':'High' if i<3 else 'Medium'})
        return {'tasks':tasks,'count':len(tasks),'weekly_focus':gaps[:3]}

class ResumeAgent:
    name='Resume Agent'
    def run(self,c):
        p=c['profile']; tips=[]
        if not p.get('projects'): tips.append('Add a role-aligned project with measurable outcomes.')
        if not p.get('certifications'): tips.append('Add relevant certifications, courses or verified training.')
        if len(p.get('skills','').split(','))<4: tips.append('Surface more concrete technical skills relevant to the target role.')
        tips.append('Use action verbs, evidence and measurable results for important claims.')
        health=max(35,100-len(tips)*12)
        return {'health':health,'suggestions':tips,'ats_keywords':c['skills']['required'][:8]}

class PlacementAgent:
    name='Placement Agent'
    def run(self,c):
        skill=c['skills']['coverage']; resume=c['resume_agent']['health']; level=c['profile'].get('experience_level','Beginner')
        bonus={'Beginner':0,'Intermediate':5,'Advanced':8}.get(level,0)
        readiness=min(100,round(skill*.55+resume*.25+20+bonus))
        return {'readiness':readiness,'focus':['Coding practice','Core CS revision','Project explanation','Mock interviews','Targeted applications']}

class InterviewAgent:
    name='Interview Agent'
    def run(self,c):
        role=c['profile'].get('target_role','Software Developer')
        return {'questions':[f'Explain a difficult problem you solved as a {role}.','Describe your project architecture and trade-offs.','How would you debug a production issue?','Which skill in the target role is currently your weakest and how are you improving it?','Describe a time you optimized or improved a system.']}

class ProjectAgent:
    name='Project Agent'
    def run(self,c):
        gaps=c['skills']['gaps'][:3]
        return {'projects':[{'title':f'{c["profile"].get("target_role","Career")} Portfolio Accelerator','skills':gaps or ['Testing','System Design'],'deliverable':'Build, document, test and deploy a small role-aligned application.'}]}
