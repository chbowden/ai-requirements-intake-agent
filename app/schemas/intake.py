from pydantic import BaseModel, Field


class StartSessionRequest(BaseModel):
    initial_problem: str = Field(min_length=1)


class AnswerRequest(BaseModel):
    answer: str = Field(min_length=1)


class QuestionPayload(BaseModel):
    id: str
    text: str


class SessionProgressResponse(BaseModel):
    session_id: str
    completed: bool
    answered_count: int
    total_questions: int
    next_question: QuestionPayload | None = None
    answers: dict[str, str]


class RequirementsArtifacts(BaseModel):
    problem_statement: str
    business_objective: str
    stakeholders: list[str]
    current_state_summary: str
    solution_recommendation: str
    user_stories: list[str]
    acceptance_criteria: list[str]
    open_questions: list[str]


class ArtifactGenerationResponse(BaseModel):
    session_id: str
    json_file: str
    markdown_file: str
    artifacts: RequirementsArtifacts
