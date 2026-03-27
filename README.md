# Meeting Task Assigner

Takes a meeting transcript and automatically figures out what tasks were discussed, who should do them, and when they need to be done.

## How it works

### Step 1 — Split transcript into sentences

The transcript is split into individual sentences by looking for `.` `!` `?` characters. Each sentence is then checked one by one.

```
"Sakshi fix the login bug by tomorrow. Mohit optimize the database."
        ↓
["Sakshi fix the login bug by tomorrow.", "Mohit optimize the database."]
```

---

### Step 2 — Is this sentence a task? (extractor.py)

Every sentence goes through 3 checks:

**Check 1 — Does it mention a team member's name?**
Uses a custom `has_word()` function. Simple `"fix" in text` would also match inside words like "prefix", so `has_word()` checks that there is no letter before or after the word.

```python
def has_word(text, word):
    i = text.find(word)
    while i != -1:
        before = (i == 0) or (not text[i - 1].isalpha())
        after  = (i + len(word) == len(text)) or (not text[i + len(word)].isalpha())
        if before and after:
            return True
        i = text.find(word, i + 1)
    return False
```

**Check 2 — Does it have an action verb?**
A hand-written list of task verbs is checked — `fix`, `update`, `design`, `test`, `optimize`, `write`, `deploy`, etc.

**Check 3 — Does it have a task phrase?**
Phrases like `we need to`, `someone should`, `we should`, `can you` are checked using simple `in` operator.

If any combination matches → sentence is a task.

Some sentences are skipped even if they match — like `"hi everyone"`, `"this can wait"`, `"it's affecting"` — these are context sentences, not tasks.

---

### Step 3 — Extract deadline, priority, dependency

The sentence + next 2 sentences are combined as context window. This is because deadline is usually said right after the task:

```
"Fix the login bug."              ← task sentence
"This needs to be done by tomorrow evening."  ← deadline is here
```

**Priority** — keywords like `critical`, `blocking`, `urgent` → Critical. `high priority`, `important` → High. Default is Medium.

**Deadline** — phrases like `tomorrow evening`, `by friday`, `end of this week`, `next monday` are matched using simple `in` operator.

**Dependency** — phrases like `depends on`, `blocked by` are found, then the hint words after them are matched against existing task descriptions.

```
"This depends on the login bug fix"
        ↓
hint words = ["login", "bug", "fix"]
        ↓
matches Task #1 "Fix the critical login bug"
        ↓
dependency = "Depends on Task #1"
```

---

### Step 4 — Clean the description

Name mentions and filler words are removed from the sentence to get a clean task description.

```
"Sakshi, we need someone to fix the critical login bug"
        ↓  remove "Sakshi," and "we need someone to"
"Fix the critical login bug"
```

---

### Step 5 — Assign task to a member (assigner.py)

**Rule 1 — Name directly mentioned → assign to that person**

```
"Sakshi fix the login bug" → assigned to Sakshi
```

**Rule 2 — No name mentioned → keyword score matching**

6 skill categories are defined: `frontend`, `backend`, `design`, `qa`, `devops`, `data`. Each has a list of keywords.

For every task and every member, count how many keywords from each category appear in their text. Then multiply the counts — this gives a match score.

```
Task: "update the API documentation"
  backend keywords found: api, documentation → backend score = 2

Mohit skills: "Database, APIs, Performance optimization"
  backend keywords found: api, database, optimization → backend score = 3

Score = 2 × 3 = 6  ✓ highest → assigned to Mohit

Sakshi skills: "React, JavaScript, UI bugs"
  backend keywords found: none → backend score = 0

Score = 2 × 0 = 0  ✗
```

Whoever has the highest score gets the task. If all scores are 0, first member is assigned as fallback.

---

### No libraries used

`extractor.py` and `assigner.py` have zero imports. Everything is done with basic Python string methods:

- `.find()` — locate a word in text
- `.lower()` — case insensitive comparison
- `.startswith()` — check sentence beginning
- `.split()` — break text into words
- `.strip()` — remove extra spaces
- `.endswith()` — check sentence ending

No regex, no NLP library, no ML model, no AI API — pure logic from scratch.

---

## Setup

```bash
pip install flask
```

## Run

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

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
task/
├── app.py          - Flask server
├── extractor.py    - reads transcript, finds tasks
├── assigner.py     - assigns tasks to team members
├── test.py         - run this to test without starting the server
├── transcript.txt  - sample transcript
├── team.json       - sample team members
└── templates/
    └── index.html  - web UI
```
