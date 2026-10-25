from pathlib import Path
import json, re
from typing import Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr, field_validator
from app.services.document_extractor import extract_document
from app.services.skill_extractor import extract_skills, CATEGORIES
from app.repositories.profile_repository import all_profiles, get_profile, save_profile, add_assessment, recent_assessments
from app.utils.scoring import readiness, match
from app.utils.skill_aliases import canonical_key

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data'
def load_json(name, fallback):
    try: return json.loads((DATA/name).read_text(encoding='utf-8'))
    except Exception: return fallback
CANDIDATES=load_json('sample_candidates.json', [])
JOBS=load_json('sample_job_descriptions.json', [])
COMPANY_DATA=load_json('talent_check_company_skillsets.json', {"source":"Illustrative demo expectations","companies":{}})
app=FastAPI(title='RADIX TalentMatch API',version='1.0.0',description='Local-first, rule-based candidate readiness and job matching demo.')
origins=[x.strip() for x in __import__('os').getenv('CORS_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(',')]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])

class Profile(BaseModel):
    id: str|None=None
    name: str=Field(min_length=1,max_length=120)
    email: str|None=None
    education: list[str]=[]
    skills: list[dict[str,Any]]=[]
    projects: list[str]=[]
    hackathons: list[str]=[]
    internships: list[str]=[]
    certifications: list[str]=[]
    preferred_roles: list[str]=[]
    cv_file: str|None=None
    @field_validator('email')
    @classmethod
    def email_ok(cls,v):
        if v and not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$',v): raise ValueError('Enter a valid email address')
        return v
class MatchRequest(BaseModel):
    candidate_id: str
    job_description_id: str|None=None
    job_description: str|None=None
class TalentRequest(BaseModel):
    candidate_id: str
    company: str

def ensure_seed():
    existing={p['id'] for p in all_profiles()}
    for candidate in CANDIDATES:
        if candidate['id'] not in existing: save_profile(candidate)
ensure_seed()

def find_candidate(pid):
    profile=get_profile(pid)
    if not profile: raise HTTPException(404,'Candidate profile not found.')
    return profile

def infer_title(text):
    for line in text.splitlines()[:8]:
        if re.search(r'\b(engineer|analyst|scientist|developer|associate|manager|intern|designer)\b',line,re.I): return line.strip()[:120]
    return 'Not detected'

@app.get('/api/health')
def health(): return {'status':'ok','version':'1.0.0'}
@app.get('/api/candidates')
def candidates(): return all_profiles()
@app.get('/api/jobs')
def jobs(): return JOBS
@app.get('/api/companies')
def companies(): return {'companies':list(COMPANY_DATA.get('companies',{}).keys()),'source':COMPANY_DATA.get('source','Illustrative fallback data')}
@app.get('/api/assessments')
def assessments(limit: int=50): return recent_assessments(limit)

@app.post('/api/jd/analyze')
async def analyze_jd(file: UploadFile|None=File(default=None), text: str|None=Form(default=None)):
    if file:
        raw=await file.read(); content=extract_document(file.filename or '',raw); filename=file.filename
    elif text and text.strip(): content=text.strip(); filename='pasted-text'
    else: raise HTTPException(422,'Upload a PDF, DOCX, or TXT file, or provide job-description text.')
    skills=extract_skills(content)
    company=next((c for c in ['Google','Microsoft','Oracle'] if re.search(rf'\b{c}\b',content,re.I)),'Not detected')
    return {'title':infer_title(content),'company':company,'source_file':filename,'text':content,'required_skills':skills,'skill_categories':CATEGORIES,'method':'Deterministic keyword/phrase extraction; no LLM used.'}

@app.post('/api/resume/parse')
async def parse_resume(file: UploadFile|None=File(default=None), text: str|None=Form(default=None)):
    if file: content=extract_document(file.filename or '',await file.read()); filename=file.filename
    elif text and text.strip(): content=text.strip(); filename='pasted-text'
    else: raise HTTPException(422,'Upload a PDF, DOCX, or TXT file, or provide resume text.')
    name=next((line.strip() for line in content.splitlines()[:6] if line.strip() and '@' not in line and not re.search(r'^(resume|curriculum vitae)',line.strip(),re.I)),'Not detected')
    emails=re.findall(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}',content,re.I)
    def section(label):
        m=re.search(rf'{label}\s*:\s*([^\n]+)',content,re.I)
        return [x.strip() for x in re.split(r'[,;|]',m.group(1)) if x.strip()] if m else []
    skills=extract_skills(content)
    return {'name':name,'email':emails[0] if emails else None,'education':section('Education'),'skills':[dict(s,level=5) for s in skills],'projects':section('Projects'),'hackathons':section('Hackathons'),'internships':section('Internships'),'certifications':section('Certifications'),'preferred_roles':section('Preferred roles'),'cv_file':filename,'evidence':content[:500],'method':'Deterministic parsing and keyword extraction; review before saving.'}

@app.get('/api/profile')
def profile_get(candidate_id: str|None=None):
    items=all_profiles()
    if candidate_id: return find_candidate(candidate_id)
    return items[0] if items else None
@app.get('/api/profiles')
def profiles_get(): return all_profiles()
@app.post('/api/profile')
def profile_create(body: Profile):
    data=body.model_dump(); data['id']=data.get('id') or re.sub(r'[^a-z0-9]+','-',data['name'].lower()).strip('-')
    if get_profile(data['id']): raise HTTPException(409,'Profile ID already exists; use PUT to update it.')
    save_profile(data); return data
@app.put('/api/profile')
def profile_update(body: Profile, candidate_id: str|None=None):
    data=body.model_dump(); data['id']=candidate_id or data.get('id')
    if not data['id']: raise HTTPException(422,'Profile id or candidate_id is required for update.')
    if not get_profile(data['id']): raise HTTPException(404,'Profile not found; use POST to create it.')
    save_profile(data); return data

@app.post('/api/talent-check')
def talent_check(body: TalentRequest):
    profile=find_candidate(body.candidate_id)
    requirements=COMPANY_DATA.get('companies',{}).get(body.company)
    if requirements is None: raise HTTPException(404,'Company expectations not found.')
    score,gaps=readiness(profile,requirements)
    add_assessment('readiness',body.candidate_id,profile['name'],body.company,score)
    return {'candidate_id':body.candidate_id,'company':body.company,'expectations_source':COMPANY_DATA.get('source'),'readiness_score':score,'skillset_gap':gaps,'recommendations':[f"Improve {g['skill_name']} by {g['gap']} level(s)." for g in sorted(gaps,key=lambda x:x['gap'],reverse=True) if g['gap']>0][:5]}

@app.post('/api/skill-match')
def skill_match(body: MatchRequest):
    profile=find_candidate(body.candidate_id)
    if body.job_description_id:
        jd=next((j for j in JOBS if j['id']==body.job_description_id),None)
        if jd is None: raise HTTPException(404,'Job description not found.')
        text=jd['text']; source=jd['id']; title=jd['title']
    elif body.job_description and body.job_description.strip(): text=body.job_description.strip(); source='supplied-text'; title=infer_title(text)
    else: raise HTTPException(422,'Provide job_description_id or job_description text.')
    skills=extract_skills(text)
    score,matched,missing,recommendations=match(profile,skills)
    add_assessment('match',body.candidate_id,profile['name'],title,score)
    matched_keys={canonical_key(s['skill_name']) for s in matched}
    categories={}
    for code,label in CATEGORIES.items():
        subset=[s for s in skills if s['category_code']==code]
        if subset: categories[code]={'label':label,'required':len(subset),'matched':sum(1 for s in subset if canonical_key(s['skill_name']) in matched_keys)}
    return {'candidate_id':body.candidate_id,'jd_source_file':source,'job_title':title,'match_score':score,'matched_skills':matched,'missing_skills':missing,'category_breakdown':categories,'recommendations':recommendations,'method':'Matched required skill phrases / total extracted required skill phrases × 100.'}
