from flask import Flask,render_template,request,jsonify,session
from config import SECRET_KEY
from db import get_db
from security import hash_password,verify_password
from services import profile,save_profile,latest,save_analysis,job,chat
from orchestrator import Orchestrator
import json
app=Flask(__name__);app.secret_key=SECRET_KEY

def uid(): return session.get('user_id')
def need(): return jsonify(ok=False,error='Please log in first.'),401

def logged(): return bool(uid())

@app.get('/')
def home(): return render_template('index.html')

@app.post('/api/register')
def register():
    d=request.get_json() or {};u=d.get('username','').strip();p=d.get('password','')
    if len(u)<3 or len(p)<4:return jsonify(ok=False,error='Username must be at least 3 characters and password at least 4 characters.'),400
    try:
        with get_db() as c:
            r=c.execute('INSERT INTO users(username,password_hash) VALUES(?,?)',(u,hash_password(p)))
            c.execute('INSERT INTO profiles(user_id) VALUES(?)',(r.lastrowid,));session['user_id']=r.lastrowid;session['username']=u
        return jsonify(ok=True,message='Account created and logged in.')
    except Exception:return jsonify(ok=False,error='Username already exists.'),409

@app.post('/api/login')
def login():
    d=request.get_json() or {}
    with get_db() as c:r=c.execute('SELECT * FROM users WHERE username=?',(d.get('username','').strip(),)).fetchone()
    if not r or not verify_password(d.get('password',''),r['password_hash']):return jsonify(ok=False,error='Invalid username or password.'),401
    session['user_id']=r['id'];session['username']=r['username'];return jsonify(ok=True,message='Logged in.')

@app.post('/api/logout')
def logout(): session.clear();return jsonify(ok=True)

@app.get('/api/me')
def me():
    if not uid():return jsonify(logged_in=False)
    return jsonify(logged_in=True,username=session['username'],profile=profile(uid()),analysis=latest(uid()))

@app.post('/api/profile')
def prof():
    if not uid():return need()
    d=request.get_json() or {};save_profile(uid(),d);return jsonify(ok=True,profile=profile(uid()))

@app.post('/api/analyze')
def analyze():
    if not uid():return need()
    p=profile(uid())
    if not p.get('name') or not p.get('target_role'):return jsonify(ok=False,error='Please enter Name and Target Role in Student Profile.'),400
    try:
        a=Orchestrator(uid()).analyze(p);save_analysis(uid(),a);return jsonify(ok=True,analysis=a)
    except Exception as e:return jsonify(ok=False,error=f'Career Intelligence failed: {type(e).__name__}: {e}'),500

@app.get('/api/dashboard')
def dashboard():
    if not uid():return need()
    with get_db() as c:
        acts=[dict(x) for x in c.execute('SELECT agent,action,status,details,created_at FROM activities WHERE user_id=? ORDER BY id DESC LIMIT 30',(uid(),)).fetchall()]
        apps=[dict(x) for x in c.execute('SELECT company,role,status,match_score,notes,created_at FROM applications WHERE user_id=? ORDER BY id DESC LIMIT 20',(uid(),)).fetchall()]
        interviews=[dict(x) for x in c.execute('SELECT role,difficulty,score,feedback,created_at FROM interviews WHERE user_id=? ORDER BY id DESC LIMIT 10',(uid(),)).fetchall()]
        progress=[dict(x) for x in c.execute('SELECT skill,score,source,created_at FROM progress WHERE user_id=? ORDER BY id DESC LIMIT 30',(uid(),)).fetchall()]
    return jsonify(ok=True,profile=profile(uid()),analysis=latest(uid()),activity=acts,applications=apps,interviews=interviews,progress=progress)

@app.post('/api/job')
def job_api():
    if not uid():return need()
    d=request.get_json() or {};t=d.get('job_text','').strip()
    if not t:return jsonify(ok=False,error='Paste a job description first.'),400
    return jsonify(ok=True,result=job(uid(),t,profile(uid())))

@app.post('/api/chat')
def chat_api():
    if not uid():return need()
    m=(request.get_json() or {}).get('message','').strip()
    if not m:return jsonify(ok=False,error='Enter a question.'),400
    return jsonify(ok=True,**chat(uid(),m))

@app.post('/api/simulate')
def simulate():
    if not uid():return need()
    d=request.get_json() or {};target=d.get('target_role','').strip();added=[x.strip() for x in d.get('added_skills','').split(',') if x.strip()]
    from agents.agents import SkillAgent
    req=SkillAgent.roles.get(target.lower(),SkillAgent.roles['software developer']);p=profile(uid());have={x.strip().lower() for x in p.get('skills','').split(',') if x.strip()};before=round(len([s for s in req if s.lower() in have])*100/len(req));new=have|{x.lower() for x in added};g=[s for s in req if s.lower() not in new];after=round((len(req)-len(g))*100/len(req))
    with get_db() as c:c.execute('INSERT INTO simulations(user_id,target_role,added_skills,coverage_before,coverage_after,gaps_json) VALUES(?,?,?,?,?,?)',(uid(),target,', '.join(added),before,after,json.dumps(g)))
    return jsonify(ok=True,scenario={'target':target,'required':req,'added':added,'coverage_before':before,'coverage_after':after,'gaps':g})

@app.post('/api/interview/start')
def interview_start():
    if not uid():return need()
    d=request.get_json() or {};role=d.get('role') or profile(uid()).get('target_role') or 'Software Developer';difficulty=d.get('difficulty','Intermediate')
    questions=[f'Why are you interested in {role}?','Explain a project where you solved a difficult technical problem.','How would you test and debug a feature in production?','What is one trade-off you made in a project and why?',f'Which {role} skill are you improving right now?']
    return jsonify(ok=True,role=role,difficulty=difficulty,questions=questions)

@app.post('/api/interview/submit')
def interview_submit():
    if not uid():return need()
    d=request.get_json() or {};answers=d.get('answers',[]);questions=d.get('questions',[]);role=d.get('role','Software Developer');difficulty=d.get('difficulty','Intermediate')
    joined=' '.join(str(x) for x in answers);score=min(100,round(sum(1 for a in answers if len(str(a).strip())>=35)*18 + min(28,len(joined.split())//8)))
    if not answers:score=0
    fb='Strong evidence and detail. Keep practicing concise explanations.' if score>=70 else 'Add specific examples, technical reasoning and measurable outcomes to each answer.'
    with get_db() as c:c.execute('INSERT INTO interviews(user_id,role,difficulty,score,feedback,questions_json) VALUES(?,?,?,?,?,?)',(uid(),role,difficulty,score,fb,json.dumps(questions)))
    return jsonify(ok=True,result={'score':score,'feedback':fb,'strengths':['Specific examples' if score>=70 else 'Willingness to practice'],'improvements':['Add measurable outcomes','Explain technical trade-offs','Use a clear situation-action-result structure']})

@app.post('/api/projects')
def projects():
    if not uid():return need()
    d=request.get_json() or {};title=d.get('title','').strip();desc=d.get('description','').strip();skills=d.get('skills','').strip()
    if not title:return jsonify(ok=False,error='Project title is required.'),400
    with get_db() as c:c.execute('INSERT INTO projects(user_id,title,description,skills,status) VALUES(?,?,?,?,?)',(uid(),title,desc,skills,d.get('status','Planned')))
    return jsonify(ok=True)

@app.get('/api/projects')
def get_projects():
    if not uid():return need()
    with get_db() as c:r=[dict(x) for x in c.execute('SELECT * FROM projects WHERE user_id=? ORDER BY id DESC',(uid(),)).fetchall()]
    return jsonify(ok=True,projects=r)

@app.post('/api/applications')
def applications():
    if not uid():return need()
    d=request.get_json() or {}
    with get_db() as c:c.execute('INSERT INTO applications(user_id,company,role,status,match_score,notes) VALUES(?,?,?,?,?,?)',(uid(),d.get('company',''),d.get('role',''),d.get('status','Applied'),int(d.get('match_score',0) or 0),d.get('notes','')))
    return jsonify(ok=True)

@app.get('/api/applications')
def get_applications():
    if not uid():return need()
    with get_db() as c:r=[dict(x) for x in c.execute('SELECT * FROM applications WHERE user_id=? ORDER BY id DESC',(uid(),)).fetchall()]
    return jsonify(ok=True,applications=r)

@app.post('/api/progress')
def add_progress():
    if not uid():return need()
    d=request.get_json() or {};skill=d.get('skill','').strip();score=max(0,min(100,int(d.get('score',0))))
    if not skill:return jsonify(ok=False,error='Skill is required.'),400
    with get_db() as c:c.execute('INSERT INTO progress(user_id,skill,score,source) VALUES(?,?,?,?)',(uid(),skill,score,d.get('source','manual')))
    return jsonify(ok=True)

@app.get('/api/evaluation')
def evaluation():
    if not uid():return need()
    with get_db() as c:
        total=c.execute('SELECT COUNT(*) c FROM activities WHERE user_id=?',(uid(),)).fetchone()['c'];fails=c.execute("SELECT COUNT(*) c FROM activities WHERE user_id=? AND status='error'",(uid(),)).fetchone()['c'];msgs=c.execute('SELECT COUNT(*) c FROM conversations WHERE user_id=?',(uid(),)).fetchone()['c'];fb=c.execute('SELECT COUNT(*) c FROM feedback WHERE user_id=?',(uid(),)).fetchone()['c'];ints=c.execute('SELECT COUNT(*) c FROM interviews WHERE user_id=?',(uid(),)).fetchone()['c'];apps=c.execute('SELECT COUNT(*) c FROM applications WHERE user_id=?',(uid(),)).fetchone()['c']
    return jsonify(ok=True,metrics={'agent_runs':total,'agent_failures':fails,'agent_success_rate':round((total-fails)*100/total) if total else 100,'conversation_messages':msgs,'feedback_items':fb,'mock_interviews':ints,'tracked_applications':apps})

@app.post('/api/feedback')
def feedback():
    if not uid():return need()
    d=request.get_json() or {};r=d.get('rating')
    if r not in ('useful','needs-work'):return jsonify(ok=False,error='Invalid feedback.'),400
    with get_db() as c:c.execute('INSERT INTO feedback(user_id,rating,context) VALUES(?,?,?)',(uid(),r,d.get('context','')))
    return jsonify(ok=True)

@app.get('/api/report')
def report():
    if not uid():return need()
    p=profile(uid());a=latest(uid()) or {}
    with get_db() as c:
        ints=[dict(x) for x in c.execute('SELECT role,difficulty,score,feedback,created_at FROM interviews WHERE user_id=? ORDER BY id DESC LIMIT 5',(uid(),)).fetchall()]
        apps=[dict(x) for x in c.execute('SELECT company,role,status,match_score,notes,created_at FROM applications WHERE user_id=? ORDER BY id DESC LIMIT 10',(uid(),)).fetchall()]
        projs=[dict(x) for x in c.execute('SELECT title,skills,status,created_at FROM projects WHERE user_id=? ORDER BY id DESC LIMIT 10',(uid(),)).fetchall()]
    return jsonify(ok=True,report={'title':'CareerPilot AI — Career Intelligence Report','generated_for':p,'executive_summary':a.get('summary','Run Career Intelligence first.'),'skill_analysis':a.get('skills',{}),'learning_plan':a.get('learning',{}),'resume_analysis':a.get('resume_agent',{}),'placement_readiness':a.get('placement_agent',{}),'digital_twin':a.get('digital_twin',{}),'explainability':a.get('explainability',[]),'interviews':ints,'applications':apps,'projects':projs})

if __name__=='__main__':app.run(host='127.0.0.1',port=5000,debug=True)
