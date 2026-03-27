from model import predict, get_model

PRIORITY_WORDS = {
    "Critical": ["critical", "urgent", "blocking", "blocks", "blocker"],
    "High":     ["high priority", "high", "important", "asap", "before release", "release"],
    "Medium":   ["medium", "normal", "sprint", "next sprint"],
    "Low":      ["low", "whenever", "someday", "nice to have"],
}

DEADLINE_WORDS = [
    (["tomorrow evening", "by tomorrow", "tomorrow"],                "Tomorrow evening"),
    (["end of the week", "end of this week", "by end of week"],      "End of this week"),
    (["by friday", "before friday", "friday"],                       "Friday"),
    (["by wednesday", "wednesday"],                                  "Wednesday"),
    (["next monday", "by next monday"],                              "Next Monday"),
    (["next week"],                                                  "Next week"),
    (["this week"],                                                  "This week"),
    (["today"],                                                      "Today"),
]

SKIP_STARTS = [
    "hi everyone", "let's discuss", "lets discuss",
    "this week's priorities", "this weeks priorities",
    "you're good with", "youre good with",
    "didn't you work", "didnt you work",
    "this depends on", "this needs to be done",
    "this can wait", "this is high",
    "it's affecting", "its affecting",
    "it's blocking", "its blocking",
    "so let's plan", "so lets plan",
    "we should tackle",
]

DOMAIN_WORDS = [
    "optimization", "performance", "database", "backend",
    "frontend", "design", "testing", "api", "documentation", "bug",
]


def has_word(text, word):
    text = text.lower()
    word = word.lower()
    i = text.find(word)
    while i != -1:
        before = (i == 0) or (not text[i - 1].isalpha())
        after = (i + len(word) == len(text)) or (not text[i + len(word)].isalpha())
        if before and after:
            return True
        i = text.find(word, i + 1)
    return False


def split_sentences(text):
    sentences = []
    current = ""
    for ch in text:
        current += ch
        if ch in ".!?":
            s = current.strip()
            if s:
                sentences.append(s)
            current = ""
    if current.strip():
        sentences.append(current.strip())
    return sentences


def extract_tasks(transcript, member_names):
    sentences = split_sentences(transcript)
    tasks = []
    task_id = 1
    seen = []
    nb_model = get_model()

    for i, sentence in enumerate(sentences):
        lower = sentence.lower()

        skip = False
        for s in SKIP_STARTS:
            if lower.startswith(s):
                skip = True
                break
        if skip:
            continue

        rhetorical = (
            any(has_word(lower, n) for n in member_names)
            and any(kw in lower for kw in DOMAIN_WORDS)
            and lower.rstrip().endswith("right?")
        )

        if not rhetorical and predict(sentence, nb_model) == 0:
            continue

        text = sentence.strip()
        for name in member_names:
            name_lower = name.lower()
            t_lower = text.lower()
            idx = t_lower.find(name_lower)
            while idx != -1:
                end = idx + len(name)
                if end < len(text) and text[end] == ",":
                    end += 1
                while end < len(text) and text[end] == " ":
                    end += 1
                text = text[:idx] + text[end:]
                t_lower = text.lower()
                idx = t_lower.find(name_lower)

        fillers = [
            "hi everyone, ", "hi everyone. ", "also, ", "and ",
            "oh, and ", "one more thing - ", "one more thing, ",
            "we need someone to ", "we need to ", "we should ",
            "someone should ", "please ",
        ]
        t_lower = text.lower()
        for filler in fillers:
            if t_lower.startswith(filler):
                text = text[len(filler):]
                t_lower = text.lower()

        if t_lower.rstrip().endswith("right?"):
            text = text[:text.lower().rfind("right?")].strip().rstrip(",").strip()

        if " is really slow" in text.lower():
            idx = text.lower().find(" is really slow")
            text = "Optimize " + text[:idx].strip()

        description = text[:1].upper() + text[1:] if text else sentence.strip()

        if any(description.lower()[:30] == s.lower()[:30] for s in seen):
            continue
        seen.append(description)

        context = sentence
        if i + 1 < len(sentences):
            context += " " + sentences[i + 1]
        if i + 2 < len(sentences):
            context += " " + sentences[i + 2]
        ctx = context.lower()

        priority = "Medium"
        for level, words in PRIORITY_WORDS.items():
            for word in words:
                if word in ctx:
                    priority = level
                    break
            if priority != "Medium":
                break

        deadline = None
        for phrases, label in DEADLINE_WORDS:
            for phrase in phrases:
                if phrase in ctx:
                    deadline = label
                    break
            if deadline:
                break

        dependency = None
        for dep_phrase in ["depends on", "blocked by"]:
            if dep_phrase in ctx:
                idx = ctx.find(dep_phrase) + len(dep_phrase)
                hint = ctx[idx:].strip().split(".")[0].split(",")[0].strip()
                hint_words = [w for w in hint.split() if len(w) > 4]
                for t in tasks:
                    if any(w in t["description"].lower() for w in hint_words):
                        dependency = "Depends on Task #" + str(t["id"])
                        break
                if not dependency and hint:
                    dependency = "Depends on: " + hint
                break

        mentioned_name = None
        for name in member_names:
            if has_word(sentence, name):
                mentioned_name = name
                break

        tasks.append({
            "id":             task_id,
            "description":    description,
            "mentioned_name": mentioned_name,
            "priority":       priority,
            "deadline":       deadline,
            "dependency":     dependency,
        })
        task_id += 1

    return tasks
