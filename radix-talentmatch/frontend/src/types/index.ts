export type Skill = {skill_name:string;category_code:string;evidence:string;confidence:string;level?:number;candidate_evidence?:string;candidate_level?:number};
export type Profile = {id:string;name:string;email:string|null;education:string[];skills:Skill[];projects:string[];hackathons:string[];internships:string[];certifications:string[];preferred_roles:string[];cv_file:string|null};
export type Job = {id:string;title:string;company:string;text:string};
export type Analysis = {title:string;company:string;source_file:string;text:string;required_skills:Skill[];method:string};
export type MatchResult = {candidate_id:string;jd_source_file:string;job_title:string;match_score:number;matched_skills:Skill[];missing_skills:Skill[];category_breakdown:Record<string,{label:string;required:number;matched:number}>;recommendations:string[];method:string};

export type Assessment = {type:'match'|'readiness';candidate_id:string;candidate_name:string;target:string;score:number;timestamp:string};
