import json
from extractor import extract_tasks
from assigner import assign_tasks

transcript = "Hi everyone, let's discuss this week's priorities. Sakshi, we need someone to fix the critical login bug that users reported yesterday. This needs to be done by tomorrow evening since it's blocking users. Also, the database performance is really slow, Mohit you're good with backend optimization right? We should tackle this by end of this week, it's affecting the user experience. And we need to update the API documentation before Friday's release - this is high priority. Oh, and someone should design the new onboarding screens for the next sprint. Arjun, didn't you work on UI designs last month? This can wait until next Monday. One more thing - we need to write unit tests for the payment module. This depends on the login bug fix being completed first, so let's plan this for Wednesday."

members = [
    {"name": "Sakshi", "role": "Frontend Developer",  "skills": "React, JavaScript, UI bugs"},
    {"name": "Mohit",  "role": "Backend Engineer",    "skills": "Database, APIs, Performance optimization"},
    {"name": "Arjun",  "role": "UI/UX Designer",      "skills": "Figma, User flows, Mobile design"},
    {"name": "Lata",   "role": "QA Engineer",         "skills": "Testing, Automation, Quality assurance"}
]

tasks = extract_tasks(transcript, [m["name"] for m in members])
result = assign_tasks(tasks, members)
print(json.dumps(result, indent=2))
