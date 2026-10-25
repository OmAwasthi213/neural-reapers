from app.utils.skill_aliases import canonical_key


def candidate_levels(profile):
    levels = {}
    for skill in profile.get("skills", []):
        key = canonical_key(skill.get("skill_name", ""))
        try:
            level = int(skill.get("level", 0))
        except (TypeError, ValueError):
            continue
        if not 1 <= level <= 10:
            continue
        levels[key] = max(levels.get(key, 0), level)
    return levels


def readiness(profile, requirements):
    levels = candidate_levels(profile)
    gaps = []
    earned = 0
    for req in requirements:
        name = req["skill_name"]
        required = int(req["required_level"])
        candidate = levels.get(canonical_key(name), 0)
        earned += min(candidate, required) / required
        gaps.append({"skill_name": name, "category_code": req["category_code"], "required_level": required, "candidate_level": candidate, "gap": max(0, required - candidate), "status": "Met" if candidate >= required else ("Partial" if candidate else "Missing"), "explanation": f"Profile level {candidate}/10 compared with illustrative required level {required}/10."})
    score = round(100 * earned / len(requirements)) if requirements else 0
    return max(0, min(100, score)), gaps


def match(profile, required_skills):
    levels = candidate_levels(profile)
    matched, missing = [], []
    for skill in required_skills:
        key = canonical_key(skill["skill_name"])
        evidence = next((s.get("evidence", "") for s in profile.get("skills", []) if canonical_key(s.get("skill_name", "")) == key and s.get("evidence") and str(s.get("evidence", "")).strip().lower() != "added or reviewed in profile builder"), "")
        item = {**skill, "candidate_level": levels.get(key, 0), "candidate_evidence": evidence}
        (matched if key in levels else missing).append(item)
    score = round(100 * len(matched) / len(required_skills)) if required_skills else 0
    recommendations = [f"Build a project or complete focused practice in {s['skill_name']}. Add evidence to your profile." for s in missing[:5]]
    return score, matched, missing, recommendations
