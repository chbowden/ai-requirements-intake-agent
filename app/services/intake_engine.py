from dataclasses import dataclass


@dataclass(frozen=True)
class IntakeQuestion:
    id: str
    text: str


INTAKE_QUESTIONS: list[IntakeQuestion] = [
    IntakeQuestion(
        id="problem_clarification",
        text="What outcome is currently blocked by this problem?",
    ),
    IntakeQuestion(
        id="stakeholders",
        text="Who are the primary stakeholders and end users impacted?",
    ),
    IntakeQuestion(
        id="current_process",
        text="How is this process handled today, step by step?",
    ),
    IntakeQuestion(
        id="goals",
        text="What business goals should the solution achieve in the next 6-12 months?",
    ),
    IntakeQuestion(
        id="pain_points",
        text="What are the top pain points in terms of time, cost, quality, or risk?",
    ),
    IntakeQuestion(
        id="gaps",
        text="What gaps exist today in tools, data, skills, or process ownership?",
    ),
]


def get_next_question(answered_count: int) -> IntakeQuestion | None:
    if answered_count >= len(INTAKE_QUESTIONS):
        return None
    return INTAKE_QUESTIONS[answered_count]
