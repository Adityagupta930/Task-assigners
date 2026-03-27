import json
from flask import Flask, request, jsonify, render_template

from extractor import extract_tasks
from assigner import assign_tasks

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/defaults")
def defaults():
    return jsonify({
        "transcript": "Hi everyone, let's discuss this week's priorities. Sakshi, we need someone to fix the critical login bug that users reported yesterday. This needs to be done by tomorrow evening since it's blocking users. Also, the database performance is really slow, Mohit you're good with backend optimization right? We should tackle this by end of this week, it's affecting the user experience. And we need to update the API documentation before Friday's release - this is high priority. Oh, and someone should design the new onboarding screens for the next sprint. Arjun, didn't you work on UI designs last month? This can wait until next Monday. One more thing - we need to write unit tests for the payment module. This depends on the login bug fix being completed first, so let's plan this for Wednesday.",
        "members": [
            {"name": "Sakshi", "role": "Frontend Developer",  "skills": "React, JavaScript, UI bugs"},
            {"name": "Mohit",  "role": "Backend Engineer",    "skills": "Database, APIs, Performance optimization"},
            {"name": "Arjun",  "role": "UI/UX Designer",      "skills": "Figma, User flows, Mobile design"},
            {"name": "Lata",   "role": "QA Engineer",         "skills": "Testing, Automation, Quality assurance"}
        ]
    })


@app.route("/process", methods=["POST"])
def process_meeting():

    if request.is_json:
        body = request.get_json(force=True)
        members = body.get("members", [])
        transcript = body.get("transcript", "").strip()
    else:
        try:
            members = json.loads(request.form.get("members", "[]"))
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid members JSON"}), 400
        transcript = request.form.get("transcript", "").strip()

    if not members:
        return jsonify({"error": "At least one team member is required"}), 400

    if not transcript:
        return jsonify({"error": "Transcript is required"}), 400

    member_names = [m["name"] for m in members if m.get("name")]

    raw_tasks = extract_tasks(transcript, member_names)

    if not raw_tasks:
        return jsonify({"transcript": transcript, "tasks": [], "message": "No tasks found"})

    assigned = assign_tasks(raw_tasks, members)

    return jsonify({"transcript": transcript, "tasks": assigned})


if __name__ == "__main__":
    app.run(debug=False, port=5000)
