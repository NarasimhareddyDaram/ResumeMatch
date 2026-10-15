
resume_skills = ["Python", "SQL", "HTML"]
required_skills = ["Python", "SQL", "React"]

matched_skills = []
missing_skills = []

for skill in required_skills:
    if skill in resume_skills:
        matched_skills.append(skill)
    else:
        missing_skills.append(skill)


total_required = len(required_skills)

if total_required > 0:
    match_score = (len(matched_skills) / total_required) * 100
else:
    match_score = 0

print("Match score:", round(match_score, 2))

match_score = (len(matched_skills) / total_required) * 100

print("Matched skills:", matched_skills)
print("Missing skills:", missing_skills)
print("Match score:", match_score)
