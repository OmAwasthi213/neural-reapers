import re
from pydantic import BaseModel, field_validator
from app.utils.skill_aliases import canonical_key, canonical_name

CATEGORIES = {"COD":"Coding","DSA":"Data Structures & Algorithms","OOD":"Object-Oriented Design","APTI":"Aptitude","COMM":"Communication","AI":"Artificial Intelligence","CLOUD":"Cloud","SQL":"SQL","SWE":"Software Engineering","SYSD":"System Design","NETW":"Networking","OS":"Operating Systems","OTHER":"Other skills"}
# Phrase -> category. This intentionally small list is transparent and easy to extend.
TAXONOMY = {
 "Python":"COD","Java":"COD","JavaScript":"COD","JS":"COD","TypeScript":"COD","C++":"COD","C#":"COD","Go":"COD","Ruby":"COD","HTML":"COD","CSS":"COD","React":"COD","FastAPI":"COD","Spring Boot":"COD",
 "Data Structures and Algorithms":"DSA","DSA":"DSA","Algorithms":"DSA","Object-Oriented Programming":"OOD","Object-Oriented Design":"OOD","OOP":"OOD","Aptitude":"APTI","Statistics":"APTI","Communication":"COMM","Machine Learning":"AI","ML":"AI","Artificial Intelligence":"AI","Deep Learning":"AI","scikit-learn":"AI","Cloud Computing":"CLOUD","AWS":"CLOUD","Azure":"CLOUD","GCP":"CLOUD","SQL":"SQL","PostgreSQL":"SQL","MySQL":"SQL","Software Engineering":"SWE","Git":"SWE","REST APIs":"SWE","Software Testing":"SWE","System Design":"SYSD","Distributed Systems":"SYSD","Networking":"NETW","TCP/IP":"NETW","Linux":"OS","Operating Systems":"OS","Docker":"CLOUD","Power BI":"OTHER","Excel":"OTHER","Data Visualization":"OTHER","Troubleshooting":"OTHER","Problem Solving":"APTI"
}

class Skill(BaseModel):
    skill_name: str
    category_code: str
    evidence: str
    confidence: str
    @field_validator("category_code")
    @classmethod
    def valid_category(cls, value):
        if value not in CATEGORIES: raise ValueError("Unsupported category code")
        return value
    @field_validator("confidence")
    @classmethod
    def valid_confidence(cls, value):
        if value not in {"high","medium","low"}: raise ValueError("Confidence must be high, medium, or low")
        return value

def extract_skills(text: str):
    found=[]
    seen=set()
    covered=[]
    for phrase, category in TAXONOMY.items():
        pattern = r"(?<![A-Za-z0-9])" + re.escape(phrase) + r"(?![A-Za-z0-9])"
        m = re.search(pattern, text, re.I)
        if not m: continue
        if any(a <= m.start() and m.end() <= b for a,b in covered): continue
        key=canonical_key(phrase)
        if key in seen: continue
        seen.add(key)
        covered.append((m.start(),m.end()))
        start=max(0,text.rfind("\n",0,m.start())+1); end=text.find("\n",m.end()); end=len(text) if end<0 else end
        evidence=text[start:end].strip()[:240] or text[max(0,m.start()-60):m.end()+60]
        found.append(Skill(skill_name=canonical_name(phrase),category_code=category,evidence=evidence,confidence="high" if len(phrase)>3 else "medium").model_dump())
    return found
