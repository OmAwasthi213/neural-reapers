# RADIX TalentMatch

RADIX TalentMatch is a local-first, AI-assisted (rule-based by default) candidate readiness and job matching MVP. It combines resume text extraction, job-description analysis, editable candidate profiles, illustrative company readiness checks, and deterministic job matching. No paid API key or Supabase account is required.

> **Demo-data notice:** all candidates and job descriptions are synthetic. Company expectations in `data/talent_check_company_skillsets.json` are illustrative examples, not official hiring criteria. Replace this JSON with an organizer-provided snapshot before presenting company scores as official.

## Features

- Dashboard with profile snapshots, live match/readiness metrics, recent data state, and skill chart.
- JD Analytics: select a sample, paste text, or upload PDF/DOCX/TXT; extract skill phrases, categories, and source evidence.
- Resume Parser: extract text from PDF/DOCX/TXT and detect name, email, education, skills, projects, hackathons, internships, and certifications. Review before transferring.
- Profile Builder: edit individual demo profiles, skills and repeated list entries; persist profiles to local SQLite.
- Talent Check: compare a selected candidate with Google, Microsoft, or Oracle illustrative requirement levels.
- Skill Matching: compare selected candidate against selected job; recalculates on changes, exposes profile/job evidence, supports CSV/print/copy reports, and offers a same-job 2–3 candidate comparison.
- Personalized four-week (30-day) gap roadmap with locally persisted checkboxes and an explicitly hypothetical score simulator.
- SQLite-backed recent assessment history on Overview; local CSV exports and browser print-to-PDF.
- FastAPI docs at `/docs`; CORS configured for local Vite development.

## Stack and layout

- Frontend: React, TypeScript, Vite, React Router, Tailwind CSS, Lucide, Recharts.
- Backend: Python, FastAPI, Pydantic, Uvicorn, PyMuPDF, python-docx, pytest.
- Storage: SQLite for editable profiles; JSON files for seeded demo data and company snapshots.
- Analysis: explicit phrase dictionary with word boundaries and evidence snippets. No LLM is called.

```text
radix-talentmatch/
  backend/app/{main.py,services,utils,repositories}
  backend/tests/test_api.py
  data/{sample_candidates.json,sample_job_descriptions.json,talent_check_company_skillsets.json}
  data/sample_jds/  data/sample_resumes/
  docs/{architecture.md,api_reference.md,testing.md}
  frontend/src/{App.tsx,pages/Modules.tsx,services/api.ts,types,index.css}
  frontend/{package.json,vite.config.ts,tsconfig.json}
  README.md
```

## Prerequisites

- Windows 10/11, macOS, or Linux.
- Python 3.10+ (Windows launcher `py` supported) and Node.js 18+ with npm.
- Internet access for initial dependency installation. Runtime analysis is local.
- VS Code is optional.

## Windows setup (PowerShell)

Open two PowerShell terminals in the project root. The commands use the Python executable directly, so activation-policy changes are not required.

### Backend terminal

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

If `py` is unavailable, replace it with `python`. Open <http://localhost:8000/docs> to inspect the API.

### Frontend terminal

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal (usually <http://localhost:5173>). The frontend API defaults to `http://localhost:8000`.

### Linux/macOS quick start

Backend: `cd backend && python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt && .venv/bin/python -m uvicorn app.main:app --reload --port 8000`.
Frontend in another terminal: `cd frontend && npm install && npm run dev`.

## Demo data and profiles

Sample candidates and jobs live in `data/`. On first API startup the four candidates are inserted into `backend/profiles.db`. Select any candidate in Profile Builder to view and edit. Updates persist locally. To reset demo profiles, stop the backend and delete `backend/profiles.db`; restarting seeds candidates again. Set `RADIX_DB_PATH` to choose another SQLite file.

Sample text resumes are in `data/sample_resumes/`; sample job-description text is in `data/sample_jds/`. File uploads support `.pdf`, `.docx`, and `.txt`, up to 8 MB. Scanned/image-only PDFs may return no text because OCR is not bundled.

## Using the modules

1. **Overview:** see seeded candidate/profile count and computed scores, with links to the modules.
2. **JD Analytics:** select a sample job, paste text, or upload a document; analyze and review detected skills and evidence.
3. **Resume Parser:** upload or paste a resume; inspect extracted fields, then transfer into Profile Builder.
4. **Profile Builder:** choose a candidate, edit line-separated fields and skill levels (`Skill|level`), and save. The save writes to SQLite.
5. **Talent Check:** choose candidate and company, then run the readiness comparison. Read the demo-data warning.
6. **Skill Matching:** select candidate and job. Result recalculates on either change; the Recalculate button can rerun it.

## Scoring and extraction

Skill levels are the explicit 1–10 values stored in profile skills; a skill absent from the profile is level 0 for comparison. Talent readiness is the average of each requirement's capped level ratio: `100 × average(min(candidate_level, required_level) / required_level)`, rounded to the nearest integer. The skill-match score is `100 × matched required skill phrases / extracted required skill phrases`, rounded to an integer. A rated profile skill is matched using a small explicit alias map: DSA/Data Structures and Algorithms, OOP/Object-Oriented Programming, JS/JavaScript, and ML/Machine Learning. Java remains distinct from JavaScript; React remains distinct from JavaScript; PostgreSQL/MySQL remain distinct from the SQL skill. Detected skills without an explicit 1–10 profile rating remain unassessed and do not count as matches or readiness evidence. The scoring formula is unchanged. Missing skills are required phrases absent from the rated profile; recommendations suggest practice/project evidence. If no skills are extracted, the job score is 0.

The extractor uses a transparent dictionary and boundary-aware phrase matching, not an LLM. Evidence is copied from the matched source line. Confidence is a simple heuristic; review analysis before relying on it.

## Replacing illustrative company expectations

Edit `data/talent_check_company_skillsets.json` to provide a `companies` object with company names and lists of `{skill_name, category_code, required_level}` entries. Levels must be 1–10 and category codes should use the taxonomy listed in `docs/architecture.md`. Keep the `source` text accurate. Restart the backend to reload the file. The scoring function reads the JSON; company requirements are not embedded in the scoring logic.

## Configuration

Copy `.env.example` / `backend/.env.example` / `frontend/.env.example` as needed. The frontend accepts `VITE_API_BASE_URL`; the backend accepts `RADIX_DB_PATH` and comma-separated `CORS_ORIGINS`. Do not add secrets to the project. No external API credentials are used.

## API endpoints

- `GET /api/health`, `/api/candidates`, `/api/jobs`, `/api/companies`, `/api/assessments`
- `POST /api/jd/analyze` (multipart file or text form)
- `POST /api/resume/parse` (multipart file or text form)
- `GET /api/profile?candidate_id=...`, `GET /api/profiles`
- `POST /api/profile` to create, `PUT /api/profile?candidate_id=...` to update
- `POST /api/talent-check` with `{candidate_id, company}`
- `POST /api/skill-match` with `{candidate_id, job_description_id}` or supplied text

Interactive OpenAPI documentation is available at <http://localhost:8000/docs>.

## Tests

```powershell
cd backend
py -m pip install -r requirements.txt
py -m pytest -q
```

The tests use an isolated temporary SQLite database. See `docs/testing.md` for coverage notes.

## Limitations / future improvements

- The extraction dictionary is intentionally small and deterministic; it can miss synonyms or infer an imperfect title. It is not AI/LLM processing.
- Scanned PDFs need OCR not included in the MVP. Resume sections are parsed with simple labels and line rules.
- Skill levels and company levels are demo inputs, not validated assessments or official company criteria.
- The storage repository is local SQLite. A repository interface boundary can be used to integrate Supabase later.
- Authentication, multi-user access control, production deployment, and document retention controls are out of scope.
- The taxonomy is intentionally small; aliases only cover explicit equivalents and do not provide semantic matching. The roadmap is heuristic and its checklist is stored in browser localStorage on that device. Browser print opens the native print dialog; PDF creation is user-controlled. Assessment history is stored in local SQLite and can be cleared by deleting the database file.


## Guided UI workflow

The enhanced interface includes a five-step rail across JD Analytics, Resume Parser, Profile Builder, Talent Check, and Skill Matching. After each successful step, a continue action leads to the next module; Resume Parser transfers reviewed extraction into Profile Builder, and saved profiles carry into both assessments. The rail and sidebar also let you jump directly between modules.

JD and resume uploads support drag-and-drop and backend parsing; Resume Parser can also build a synthetic sample resume from a selected saved candidate and submit it to the same parser API. Results include working search/category filters, expandable evidence, category charts, and explicit reset/retry states. Profile Builder supports new profiles, add/remove list-entry controls, cancel confirmation, save confirmation, and SQLite persistence. Candidate/job changes clear stale match results and trigger API recalculation. The dashboard reports current live calculations and sample-role availability, not fabricated assessment history.


## Comparison, roadmap, exports, and history

Skill Matching can compare two or three synthetic profiles against one job using the same `/api/skill-match` endpoint and score returned for individual matching. The comparison CSV includes actual API results, matched/missing skills, and available evidence. The individual result can be downloaded as CSV, printed/saved as PDF through the browser print dialog, or copied as a concise summary.

The 30-day roadmap is derived from the current result's missing skills, split into four weekly practice/project milestones. Task completion persists in browser localStorage, separately from proficiency ratings; the what-if score is hypothetical and does not edit a profile. Successful Talent Check and Skill Match API calls append timestamped events to SQLite and appear on Overview.

Resume skill detection does not assign a proficiency rating. In Profile Builder, enter a 1–10 level explicitly and optionally add source evidence as a fourth pipe-separated value: `Python | 7 | COD | Built a Python project`. A missing/zero rating is unassessed. All scores remain deterministic, explainable estimates—not verified expertise or automated hiring decisions.
