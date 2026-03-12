import json
from datetime import UTC, datetime
from pathlib import Path

from app.schemas.intake import RequirementsArtifacts


def generate_artifacts(answers: dict[str, str]) -> RequirementsArtifacts:
    initial_problem = answers.get("initial_problem", "").strip()
    clarification = answers.get("problem_clarification", "").strip()
    stakeholders_raw = answers.get("stakeholders", "").strip()
    current_process = answers.get("current_process", "").strip()
    goals = answers.get("goals", "").strip()
    pain_points = answers.get("pain_points", "").strip()
    gaps = answers.get("gaps", "").strip()

    stakeholders = _split_stakeholders(stakeholders_raw)
    recommendation = _recommend_solution_type(" ".join(answers.values()))

    problem_statement = (
        f"{initial_problem} Impact: {clarification}"
        if clarification
        else initial_problem
    ).strip()

    current_state_summary = " ".join(
        part for part in [current_process, pain_points, gaps] if part
    ).strip()

    business_objective = goals or clarification or "Define measurable business outcomes."

    stories = _build_user_stories(stakeholders, business_objective, current_process)
    criteria = _build_acceptance_criteria(recommendation)
    open_questions = _build_open_questions(stakeholders, gaps, goals)

    return RequirementsArtifacts(
        problem_statement=problem_statement,
        business_objective=business_objective,
        stakeholders=stakeholders,
        current_state_summary=current_state_summary,
        solution_recommendation=recommendation,
        user_stories=stories,
        acceptance_criteria=criteria,
        open_questions=open_questions,
    )


def write_artifacts(
    session_id: str, artifacts: RequirementsArtifacts, output_dir: Path
) -> tuple[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    base_name = f"requirements_{session_id}_{timestamp}"

    json_path = output_dir / f"{base_name}.json"
    markdown_path = output_dir / f"{base_name}.md"

    json_path.write_text(
        json.dumps(artifacts.model_dump(), indent=2),
        encoding="utf-8",
    )
    markdown_path.write_text(_to_markdown(artifacts), encoding="utf-8")

    return str(json_path), str(markdown_path)


def _split_stakeholders(raw_value: str) -> list[str]:
    candidates = [item.strip() for item in raw_value.split(",")]
    cleaned = [item for item in candidates if item]
    return cleaned or ["TBD Stakeholder"]


def _recommend_solution_type(all_text: str) -> str:
    text = all_text.lower()
    if any(keyword in text for keyword in ["predict", "model", "llm", "ai", "ml"]):
        return "AI"
    if any(
        keyword in text
        for keyword in ["manual", "repetitive", "copy", "workflow", "approval", "rpa"]
    ):
        return "automation"
    if any(
        keyword in text for keyword in ["dashboard", "report", "metrics", "kpi", "bi"]
    ):
        return "reporting"
    if any(
        keyword in text for keyword in ["handoff", "process", "policy", "ownership"]
    ):
        return "process improvement"
    return "unclear"


def _build_user_stories(
    stakeholders: list[str], business_objective: str, current_process: str
) -> list[str]:
    primary_actor = stakeholders[0] if stakeholders else "business user"
    return [
        (
            f"As a {primary_actor}, I want a guided intake workflow so that "
            f"I can capture complete requirements aligned to {business_objective}."
        ),
        (
            "As an implementation lead, I want standardized requirement artifacts "
            f"so that we can reduce ambiguity in the current state ({current_process or 'to be defined'})."
        ),
    ]


def _build_acceptance_criteria(solution_recommendation: str) -> list[str]:
    return [
        "The system captures an initial business problem and all structured follow-up answers.",
        "The system returns a clear problem statement and business objective.",
        "The output includes stakeholders and a current-state summary.",
        f"The output includes a solution recommendation categorized as {solution_recommendation}.",
        "The system generates exactly 2 user stories, 5 acceptance criteria, and 3 open questions.",
    ]


def _build_open_questions(
    stakeholders: list[str], gaps: str, goals: str
) -> list[str]:
    return [
        f"What measurable KPI should be used to evaluate success for {stakeholders[0]}?",
        f"Which gap should be prioritized first: {gaps or 'tools, data, or process'}?",
        f"What is the delivery timeline and milestone target for this goal: {goals or 'TBD'}?",
    ]


def _to_markdown(artifacts: RequirementsArtifacts) -> str:
    stakeholder_lines = "\n".join(f"- {item}" for item in artifacts.stakeholders)
    story_lines = "\n".join(f"- {item}" for item in artifacts.user_stories)
    criteria_lines = "\n".join(f"- {item}" for item in artifacts.acceptance_criteria)
    question_lines = "\n".join(f"- {item}" for item in artifacts.open_questions)

    return (
        "# Requirements Intake Artifacts\n\n"
        f"## Problem Statement\n{artifacts.problem_statement}\n\n"
        f"## Business Objective\n{artifacts.business_objective}\n\n"
        "## Stakeholders\n"
        f"{stakeholder_lines}\n\n"
        "## Current-State Summary\n"
        f"{artifacts.current_state_summary}\n\n"
        "## Solution Recommendation\n"
        f"{artifacts.solution_recommendation}\n\n"
        "## User Stories\n"
        f"{story_lines}\n\n"
        "## Acceptance Criteria\n"
        f"{criteria_lines}\n\n"
        "## Open Questions\n"
        f"{question_lines}\n"
    )
