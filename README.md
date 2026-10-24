# neural-reapers
this is the premium project for the premium placement drive hackathon 1
# RADIX TalentMatch

**An AI-powered job readiness and skill-matching platform for candidates.**

TalentMatch helps candidates understand how well their skills align with a company's expectations and a specific job description. It extracts skills from resumes and job descriptions, builds a structured candidate profile, calculates job readiness, and identifies skill gaps with actionable explanations.

## 1. Problem Statement

Candidates often struggle to determine whether they are ready for a particular role, which skills they lack, and what they should improve before applying.

TalentMatch addresses this problem by combining AI-powered document analysis with transparent, data-driven skill assessment.

## 2. Objectives

- Extract required skills and technologies from job descriptions.
- Parse resumes into structured skills, education, projects, and experience.
- Build and save comprehensive candidate profiles.
- Assess readiness against company-specific skill expectations.
- Match candidates to individual job descriptions and explain missing skills.

## 3. Core Features

| Module | Functionality |
|---|---|
| JD Analytics | Upload PDF/DOCX job descriptions and extract categorized requirements. |
| Resume Parsing | Extract skills, education, projects, and experience from resumes. |
| Profile Builder | Create, edit, and save candidate profiles, including certifications, internships, hackathons, and preferred roles. |
| Talent Check | Compare a candidate's skill levels against company expectations across 12 categories. |
| Skill Matching | Calculate job-specific match scores and display matched and missing skills. |

## 4. Technology Stack

- **Frontend:** React
- **Backend:** Python, FastAPI
- **AI and NLP:** LangChain with an available LLM provider
- **Document Processing:** PDF and DOCX text extraction libraries
- **Database:** Supabase for persistent storage
- **Data Exchange:** JSON REST APIs
- **Version Control:** Git and GitHub

Keep scoring and profile-management logic deterministic wherever possible. Use LLMs for semantic extraction and interpretation, not for arbitrary score generation.

## 5. System Architecture

```text
                React Frontend
                      |
                FastAPI Backend
                      |
        +-------------+-------------+
        |             |             |
    JD Analytics  Resume Parser  Profile Builder
        |             |             |
        +-------------+-------------+
                      |
              Candidate Profile
                      |
              +-------+-------+
              |               |
          Talent Check   Skill Matching
              |               |
        Company Data      Extracted JD
              |               |
              +-------+-------+
                      |
            Scores, Gaps & Insights
                      |
             React Results UI
```

### Proposed repository structure

```text
radix-talentmatch/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── jd_analytics.py
│   │   │   ├── resume_parser.py
│   │   │   ├── profile_builder.py
│   │   │   ├── talent_check.py
│   │   │   └── skill_matching.py
│   │   └── utils/
│   └── requirements.txt
├── data/
│   ├── sample_jds/
│   ├── sample_resumes/
│   └── talent_check_company_skillsets.json
├── tests/
├── .env.example
├── .gitignore
└── README.md
```

## 6. Shared Data Contract

All modules must follow one agreed JSON schema so that integration remains consistent.

### Skill object

```json
{
  "skill_name": "Python",
  "category_code": "COD",
  "evidence": "Developed Python-based projects",
  "confidence": "high"
}
```

Allowed categories:

- `COD` — Coding
- `DSA` — Data Structures and Algorithms
- `OOD` — Object-Oriented Design
- `APTI` — Aptitude
- `COMM` — Communication
- `AI` — Artificial Intelligence
- `CLOUD` — Cloud
- `SQL` — SQL
- `SWE` — Software Engineering
- `SYSD` — System Design
- `NETW` — Networking
- `OS` — Operating Systems
- `OTHER` — Skills outside the 12 categories

### Candidate profile

```json
{
  "name": "Candidate Name",
  "email": "candidate@example.com",
  "education": "B.Tech Computer Science",
  "skills": [],
  "hackathons": [],
  "internships": [],
  "certifications": [],
  "preferred_roles": [],
  "cv_file": ""
}
```

### Assessment results

Talent Check must return the company, category-wise required and candidate levels, gaps, and readiness score.

Skill Matching must return the JD reference, match score, matched skills, missing skills, and supporting evidence.

The full schemas, validation rules, and field types must be agreed upon by all five developers before implementation.

## 7. Implementation Plan

### Phase 1 — Setup and contract

- Form the five-member team and assign one role per member.
- Appoint a Scrum Master.
- Review the supplied JDs, resumes, and company skillset data.
- Finalize shared schemas, API interfaces, and repository structure.
- Establish the development environment and Git workflow.

### Phase 2 — Independent development

Each member develops and tests their module independently.

- **Role 1:** JD document extraction and skill categorization.
- **Role 2:** Resume extraction and structured candidate data.
- **Role 3:** Profile form, validation, editing, and save/load functionality.
- **Role 4:** Company readiness scoring and skill-gap analysis.
- **Role 5:** Job-specific skill matching and missing-skill explanations.

Use sample data and mocked module outputs to avoid blocking dependent developers.

### Phase 3 — Integration

Connect the modules through shared JSON schemas and backend APIs.

Implement the end-to-end workflow:

1. Select or upload a job description.
2. Upload a resume and extract candidate information.
3. Create or update the candidate profile.
4. Select a company and run Talent Check.
5. Run Skill Matching against the selected JD.
6. Display scores, matched skills, missing skills, and recommendations.

### Phase 4 — Testing and refinement

- Test each module independently against at least two sample JDs or resumes.
- Validate file handling, JSON schemas, API responses, and error handling.
- Compare multiple candidates to verify that scores and skill gaps differ appropriately.
- Test at least one complete candidate-to-job workflow.
- Improve the UI, loading states, and result explanations.

### Phase 5 — Demo preparation

- Prepare a reliable sample workflow.
- Rehearse the complete live demonstration.
- Prepare architecture diagrams, key design decisions, and one technical challenge with its solution.
- Freeze features and resolve critical bugs before the deadline.

## 8. Scoring Methodology

### Talent Check

Compare the candidate's level against the selected company's expected level for each skill category.

A simple normalized readiness score is:

`Readiness = 100 × weighted achieved skill points / weighted required skill points`

Only categories with defined company requirements should contribute to the denominator. Document the weighting, level-assignment method, and handling of missing evidence.

### Skill Matching

Match extracted JD requirements against candidate skills using normalized names, aliases, fuzzy matching, or semantic similarity.

`Match Score = 100 × matched requirement weight / total requirement weight`

Keep missing skills visible even when the overall score is high. Distinguish explicitly demonstrated skills from inferred or uncertain skills, and do not claim that a match score predicts hiring success.

## 9. Required Inputs and Resources

Before development begins, ensure the team has:

- Six sample job descriptions across Google, Microsoft, and Oracle Financial Services.
- Four sample resumes.
- `talent_check_company_skillsets.json` containing company-specific expectations.
- Access to an LLM provider and its configured API credentials.
- Supabase project credentials.
- The agreed JSON schemas and milestone checklist.

Use `.env` for secrets and commit only `.env.example`. Never commit API keys, database credentials, or unnecessary personal information from resumes.

## 10. Definition of Done

The project is complete when:

- All five modules run independently.
- The integrated application processes at least one complete candidate–company–job combination.
- Talent Check and Skill Matching produce meaningfully different results for different candidates.
- Scores include understandable explanations and skill gaps.
- Input validation and basic error handling work.
- The application can be demonstrated end to end without developer intervention.

## 11. Team Responsibilities

| Role | Primary ownership |
|---|---|
| Role 1 | JD Analytics |
| Role 2 | Resume Parsing |
| Role 3 | Profile Builder |
| Role 4 | Talent Check |
| Role 5 | Skill Matching |

The Scrum Master owns one of these roles as well as coordination, progress tracking, dependency management, integration, and presentation readiness.

## 12. Hackathon Timeline

| Date | Milestone |
|---|---|
| 24 October | Team setup, role allocation, schemas, and initial implementation |
| 25–27 October | Module development, testing, and integration |
| 28 October | Final testing, bug fixes, and presentation freeze |
| 29 October | Peer presentations — top 9 teams selected |
| 30 October | Expert panel — top 3 teams selected |
| 31 October | TGL Blitz grand finale |

**Priority:** Deliver a reliable end-to-end product with transparent skill-gap explanations before adding advanced AI features or unnecessary complexity.

---

*RADIX TalentMatch Hackathon · October 2026*
