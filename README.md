# Meeting Task Assigner

Takes a meeting transcript and automatically identifies tasks, assigns them to the right team members, and extracts deadlines, priorities, and dependencies.

## How it works

### Task Detection — Naive Bayes Model (model.py + data.py)

A Naive Bayes classifier is trained from scratch on 100 labeled sentences — 60 task sentences and 40 non-task sentences. No external library is used. The model trains automatically when the app starts.

For every sentence in the transcript, the model calculates the probability of it being a task or not, and decides accordingly.

### Task Assignment — Keyword Scoring (assigner.py)

6 skill categories are defined: frontend, backend, design, qa, devops, data. Each has a list of keywords.

For every task and every member, keyword matches are counted per category. The counts are multiplied to get a match score. The member with the highest score gets the task.

If a member's name is directly mentioned in the transcript, they are assigned immediately without scoring.

### Deadline, Priority, Dependency — String Matching (extractor.py)

The sentence plus the next 2 sentences are used as context. Priority keywords like `critical`, `blocking`, `urgent` are matched. Deadline phrases like `tomorrow evening`, `by friday`, `next monday` are matched. Dependency phrases like `depends on`, `blocked by` are matched against existing task descriptions.

### No libraries used in core logic

`extractor.py`, `assigner.py`, and `data.py` have zero imports. Everything uses basic Python string methods — `.find()`, `.lower()`, `.startswith()`, `.split()`, `.strip()`.

`model.py` uses only `json`, `os`, and `pickle` (Python built-ins) to save and load the trained model as `model.pkl`.

Only `flask` is used in `app.py` for the web server.

---

## Setup

```bash
pip install flask
```

## Run

```bash
python app.py
```

Open `http://localhost:5000`

## Send data as JSON

```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Sakshi fix the login bug by tomorrow. Mohit optimize the database by end of week.",
    "members": [
      {"name": "Sakshi", "role": "Frontend Developer", "skills": "React, JavaScript"},
      {"name": "Mohit",  "role": "Backend Engineer",   "skills": "Database, Performance"}
    ]
  }'
```

## Files

```
Task-assigner/
├── app.py           - Flask server
├── extractor.py     - splits transcript, detects tasks, extracts deadline/priority/dependency
├── assigner.py      - assigns tasks to members using keyword scoring
├── model.py         - Naive Bayes classifier trained from scratch, saved as model.pkl
├── model.pkl        - saved trained model (auto-generated on first run)
├── data.py          - 100 labeled training sentences
├── test.py          - test without starting the server
├── requirements.txt
└── templates/
    └── index.html   - web UI
```
