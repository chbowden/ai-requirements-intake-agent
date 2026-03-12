const form = document.getElementById("intake-form");
const problemField = document.getElementById("problem");
const questionFlow = document.getElementById("question-flow");
const answerForm = document.getElementById("answer-form");
const answerField = document.getElementById("answer");
const progress = document.getElementById("progress");
const currentQuestion = document.getElementById("current-question");
const artifactActions = document.getElementById("artifact-actions");
const generateArtifactsButton = document.getElementById("generate-artifacts");
const artifactOutput = document.getElementById("artifact-output");
const artifactFiles = document.getElementById("artifact-files");
const artifactJson = document.getElementById("artifact-json");
const status = document.getElementById("status");
const startButton = form.querySelector('button[type="submit"]');
const answerButton = answerForm.querySelector('button[type="submit"]');

let currentSessionId = null;

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const problem = problemField.value.trim();
  if (!problem) {
    status.textContent = "Please enter a business problem before continuing.";
    return;
  }

  status.textContent = "Starting intake session...";
  startButton.disabled = true;

  try {
    const response = await fetch("/intake/session/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ initial_problem: problem }),
    });

    if (!response.ok) {
      status.textContent = "Could not start intake session. Try again.";
      return;
    }

    const data = await response.json();
    currentSessionId = data.session_id;
    questionFlow.classList.remove("hidden");
    artifactOutput.classList.add("hidden");
    artifactActions.classList.add("hidden");
    answerForm.classList.remove("hidden");
    renderProgress(data);
    renderQuestion(data);
    status.textContent = "Session started.";
  } catch (error) {
    status.textContent = "Network error while starting intake. Try again.";
  } finally {
    startButton.disabled = false;
  }
});

answerForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const answer = answerField.value.trim();
  if (!answer) {
    status.textContent = "Please enter an answer before submitting.";
    return;
  }

  if (!currentSessionId) {
    status.textContent = "No active session. Start intake again.";
    return;
  }

  status.textContent = "Submitting answer...";
  answerButton.disabled = true;

  try {
    const response = await fetch(`/intake/session/${currentSessionId}/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer }),
    });

    if (!response.ok) {
      status.textContent = "Could not submit answer. Try again.";
      return;
    }

    const data = await response.json();
    answerField.value = "";
    renderProgress(data);
    renderQuestion(data);
  } catch (error) {
    status.textContent = "Network error while submitting answer. Try again.";
  } finally {
    answerButton.disabled = false;
  }
});

function renderProgress(data) {
  progress.textContent = `Answered ${data.answered_count} of ${data.total_questions} follow-up questions`;
}

function renderQuestion(data) {
  if (data.completed) {
    currentQuestion.textContent = "Intake questions complete. Artifact generation is next.";
    answerForm.classList.add("hidden");
    artifactActions.classList.remove("hidden");
    status.textContent = "Session complete.";
    return;
  }

  currentQuestion.textContent = data.next_question.text;
  answerForm.classList.remove("hidden");
  artifactActions.classList.add("hidden");
  status.textContent = "Next question ready.";
}

generateArtifactsButton.addEventListener("click", async () => {
  if (!currentSessionId) {
    status.textContent = "No active session. Start intake again.";
    return;
  }

  status.textContent = "Generating artifacts...";
  generateArtifactsButton.disabled = true;

  try {
    const response = await fetch(`/intake/session/${currentSessionId}/artifacts`, {
      method: "POST",
    });

    if (!response.ok) {
      status.textContent = "Artifact generation failed. Ensure intake is complete.";
      return;
    }

    const data = await response.json();
    artifactOutput.classList.remove("hidden");
    artifactFiles.innerHTML = [
      `<a href="${data.json_artifact.download_url}">${data.json_artifact.filename}</a>`,
      `<a href="${data.markdown_artifact.download_url}">${data.markdown_artifact.filename}</a>`,
    ].join(" | ");
    artifactJson.textContent = JSON.stringify(data.artifacts, null, 2);
    status.textContent = "Artifacts generated and ready to download.";
  } catch (error) {
    status.textContent = "Network error while generating artifacts. Try again.";
  } finally {
    generateArtifactsButton.disabled = false;
  }
});
