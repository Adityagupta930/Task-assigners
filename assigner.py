SKILL_CATEGORIES = {
    "frontend": ["ui", "frontend", "front-end", "react", "javascript", "css", "html", "login", "screen", "onboarding", "component", "interface", "layout", "animation", "responsive", "mobile ui", "button", "style"],
    "backend":  ["backend", "back-end", "api", "database", "db", "server", "performance", "optimization", "optimize", "query", "sql", "endpoint", "rest", "microservice", "cache", "documentation", "docs", "swagger"],
    "design":   ["design", "figma", "wireframe", "mockup", "prototype", "user flow", "ux", "ui/ux", "onboarding", "screen", "visual", "branding", "illustration", "icon", "typography", "mobile design"],
    "qa":       ["test", "testing", "unit test", "integration test", "qa", "quality", "automation", "selenium", "cypress", "jest", "pytest", "bug", "regression", "coverage", "payment"],
    "devops":   ["deploy", "deployment", "ci/cd", "docker", "kubernetes", "terraform", "jenkins", "infrastructure", "cloud", "aws", "azure", "monitoring", "logging", "scaling"],
    "data":     ["data", "analytics", "ml", "machine learning", "dataset", "etl", "spark", "pandas", "visualization", "dashboard", "report", "metric"],
}


def assign_tasks(tasks, members):
    result = []

    for task in tasks:
        assigned_member = None

        if task.get("mentioned_name"):
            for member in members:
                if member["name"].lower() == task["mentioned_name"].lower():
                    assigned_member = member
                    break

        if not assigned_member:
            task_lower = task["description"].lower()
            task_scores = {}
            for cat, keywords in SKILL_CATEGORIES.items():
                task_scores[cat] = sum(1 for kw in keywords if kw in task_lower)

            best_score = -1
            for member in members:
                member_text = (member.get("role", "") + " " + member.get("skills", "")).lower()
                member_scores = {}
                for cat, keywords in SKILL_CATEGORIES.items():
                    member_scores[cat] = sum(1 for kw in keywords if kw in member_text)

                score = sum(task_scores.get(cat, 0) * member_scores.get(cat, 0) for cat in SKILL_CATEGORIES)

                if score > best_score:
                    best_score = score
                    assigned_member = member

            if best_score == 0:
                assigned_member = members[0]

        if task.get("mentioned_name"):
            reason = "Directly mentioned in the meeting"
        else:
            task_lower = task["description"].lower()
            member_text = (assigned_member.get("role", "") + " " + assigned_member.get("skills", "")).lower()
            matched = []
            for cat, keywords in SKILL_CATEGORIES.items():
                if any(kw in task_lower for kw in keywords) and any(kw in member_text for kw in keywords):
                    matched.append(cat)
            if matched:
                reason = assigned_member["role"] + " - matched skills: " + ", ".join(matched)
            else:
                reason = "Best available match: " + assigned_member["role"]

        result.append({
            "id":          task["id"],
            "description": task["description"],
            "assigned_to": assigned_member["name"],
            "role":        assigned_member["role"],
            "deadline":    task.get("deadline"),
            "priority":    task.get("priority", "Medium"),
            "dependency":  task.get("dependency"),
            "reason":      reason,
        })

    return result
