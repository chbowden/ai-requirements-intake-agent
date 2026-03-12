from typing import Annotated

from pydantic import BaseModel, StringConstraints


NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class StartSessionRequest(BaseModel):
    initial_problem: NonEmptyText


class AnswerRequest(BaseModel):
    answer: NonEmptyText


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


class ArtifactFileResponse(BaseModel):
    filename: str
    download_url: str


class ArtifactGenerationResponse(BaseModel):
    session_id: str
    json_artifact: ArtifactFileResponse
    markdown_artifact: ArtifactFileResponse
    artifacts: RequirementsArtifacts
