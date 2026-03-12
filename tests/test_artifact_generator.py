from pathlib import Path

from app.services.artifact_generator import generate_artifacts, write_artifacts


def test_generate_artifacts_parses_stakeholders_and_recommendation() -> None:
    artifacts = generate_artifacts(
        {
            "initial_problem": "Weekly reporting is inconsistent.",
            "problem_clarification": "Leaders cannot trust pipeline metrics.",
            "stakeholders": "Sales managers, RevOps, executives",
            "current_process": "Teams export spreadsheets and consolidate them manually.",
            "goals": "Improve visibility and reduce reporting time.",
            "pain_points": "Manual rework delays updates.",
            "gaps": "No dashboard or shared workflow.",
        }
    )

    assert artifacts.stakeholders == ["Sales managers", "RevOps", "executives"]
    assert artifacts.solution_recommendation == "automation"
    assert artifacts.problem_statement.startswith("Weekly reporting is inconsistent.")
    assert len(artifacts.user_stories) == 2
    assert len(artifacts.acceptance_criteria) == 5
    assert len(artifacts.open_questions) == 3


def test_generate_artifacts_uses_defaults_for_missing_optional_values() -> None:
    artifacts = generate_artifacts({"initial_problem": "Need a better intake flow."})

    assert artifacts.stakeholders == ["TBD Stakeholder"]
    assert artifacts.business_objective == "Define measurable business outcomes."
    assert artifacts.solution_recommendation == "unclear"
    assert "TBD Stakeholder" in artifacts.open_questions[0]


def test_write_artifacts_creates_json_and_markdown_files() -> None:
    artifacts = generate_artifacts(
        {
            "initial_problem": "Need a better intake flow.",
            "stakeholders": "Product team",
            "goals": "Reduce triage time.",
        }
    )
    output_dir = Path(".tmp/artifact-generator-tests")
    output_dir.mkdir(parents=True, exist_ok=True)

    json_file, markdown_file = write_artifacts("session-123", artifacts, output_dir)

    json_path = Path(json_file)
    markdown_path = Path(markdown_file)
    assert json_path.exists()
    assert markdown_path.exists()
    assert json_path.read_text(encoding="utf-8").startswith("{")
    assert "# Requirements Intake Artifacts" in markdown_path.read_text(
        encoding="utf-8"
    )
