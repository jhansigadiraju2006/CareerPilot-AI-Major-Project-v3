import json,re
from db import get_db
from agents.agents import SkillAgent

def profile(uid):
    with get_db() as c:
        r=c.execute('SELECT * FROM profiles WHERE user_id=?',(uid,)).fetchone()
        return dict(r) if r else {}

def save_profile(uid,d):
    fields=['name','college','target_role','skills','experience_level','goals','certifications','projects']
    vals=[d.get(x,'') for x in fields]
    with get_db() as c:c.execute('UPDATE profiles SET name=?,college=?,target_role=?,skills=?,experience_level=?,goals=?,certifications=?,projects=?,updated_at=CURRENT_TIMESTAMP WHERE user_id=?',(*vals,uid))

def latest(uid):
    with get_db() as c:r=c.execute('SELECT analysis_json FROM analyses WHERE user_id=? ORDER BY id DESC LIMIT 1',(uid,)).fetchone()
    return json.loads(r['analysis_json']) if r else None

def save_analysis(uid,a):
    with get_db() as c:c.execute('INSERT INTO analyses(user_id,analysis_json) VALUES(?,?)',(uid,json.dumps(a)))

def _skills_from_text(text):
    known=set(sum(SkillAgent.roles.values(),[])); low=text.lower(); return [s for s in known if re.search(r'(?<!\w)'+re.escape(s.lower())+r'(?!\w)',low)]

def job(uid,text,p):
    required=_skills_from_text(text)
    if not required:
        required=['Communication','Problem Solving','Git','SQL']
    have={x.strip().lower() for x in p.get('skills','').split(',') if x.strip()}
    matched=[s for s in required if s.lower() in have]; gaps=[s for s in required if s.lower() not in have]
    match=round(len(matched)*100/len(required))
    r={'match':match,'required':required,'matched':matched,'gaps':gaps,'recommendation':'Prioritize the missing skills before applying.' if gaps else 'Your listed skills cover the detected requirements.'}
    with get_db() as c:c.execute('INSERT INTO job_analyses(user_id,job_text,result_json) VALUES(?,?,?)',(uid,text,json.dumps(r)))
    return r

def chat(uid,m):
    p=profile(uid);a=latest(uid); ml=m.lower()
    if 'skill' in ml or 'gap' in ml:
        ans=f"Your target is {p.get('target_role','not set')}. Current analysis shows these priority gaps: {', '.join((a or {}).get('skills',{}).get('gaps',[])[:6]) or 'Run Career Intelligence first.'}."
    elif 'resume' in ml or 'ats' in ml:
        ans=f"Your current portfolio/resume health is {(a or {}).get('resume_agent',{}).get('health','--')}%. Focus on measurable project outcomes and role-specific keywords."
    elif 'interview' in ml:
        ans='Start with the Mock Interview module. It uses your target role and skill gaps to generate role-aware questions.'
    elif 'job' in ml:
        ans='Paste a job description into Job Intelligence. The matcher extracts known skills, compares them with your profile and records the analysis.'
    else:
        ans=f"CareerPilot is tracking your goal of {p.get('target_role','choosing a career role')}. Run an analysis, then use the roadmap, simulator and interview modules to improve the next weakest area."
    with get_db() as c:
        c.execute('INSERT INTO conversations(user_id,role,message) VALUES(?,?,?)',(uid,'user',m));c.execute('INSERT INTO conversations(user_id,role,message) VALUES(?,?,?)',(uid,'assistant',ans))
    return {'answer':ans}
