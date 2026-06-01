from __future__ import annotations

from dataclasses import dataclass, field, replace
import re
from typing import Protocol

from marshal_app.domain.enums import PlanningPhase
from marshal_app.domain.models import Project
from marshal_app.integrations.gemini import GeminiClient
from marshal_app.services.project_service import ProjectService
from marshal_app.services.task_service import TaskService


@dataclass(slots=True)
class PlanningTaskDraft:
    title: str
    description: str = ""
    rationale: str = ""


@dataclass(slots=True)
class PlanningDraftResult:
    goal_summary: str
    project_description: str
    tentative_tasks: list[PlanningTaskDraft]
    clarification_question: str | None = None


@dataclass(slots=True)
class PlanningSession:
    raw_input: str
    goal_summary: str
    project_description: str
    tentative_tasks: list[PlanningTaskDraft] = field(default_factory=list)
    structured_tasks: list[PlanningTaskDraft] = field(default_factory=list)
    clarification_question: str | None = None
    phase: PlanningPhase = PlanningPhase.DRAFT
    revision_count: int = 0
    transcript: list[str] = field(default_factory=list)


class PlanningEngine(Protocol):
    def draft(self, raw_input: str) -> PlanningDraftResult:
        raise NotImplementedError


class RuleBasedPlanningEngine:
    def draft(self, raw_input: str) -> PlanningDraftResult:
        cleaned_input = self._normalize_whitespace(raw_input)
        goal_summary = self._summarize_goal(cleaned_input)
        candidate_phrases = self._extract_candidate_phrases(cleaned_input)

        tasks: list[PlanningTaskDraft] = []
        seen_titles: set[str] = set()
        for phrase in candidate_phrases:
            title = self._phrase_to_title(phrase)
            if not title:
                continue
            normalized = title.casefold()
            if normalized in seen_titles:
                continue
            seen_titles.add(normalized)
            tasks.append(
                PlanningTaskDraft(
                    title=self._shorten_task_title(title),
                    description=self._build_description(phrase),
                    rationale="Drafted from your input",
                )
            )
            if len(tasks) >= 5:
                break

        if not tasks:
            tasks = self._fallback_tasks(goal_summary)

        clarification_question = self._clarifying_question(cleaned_input, tasks)
        return PlanningDraftResult(
            goal_summary=goal_summary,
            project_description=self._summarize_project_description(goal_summary, tasks),
            tentative_tasks=tasks,
            clarification_question=clarification_question,
        )

    def _normalize_whitespace(self, raw_input: str) -> str:
        return re.sub(r"\s+", " ", raw_input).strip()

    def _summarize_goal(self, raw_input: str) -> str:
        if not raw_input:
            return "No input provided yet"
        split_source = raw_input.replace("?", ".").replace("!", ".")
        first_clause = split_source.split(".")[0].strip()
        if not first_clause:
            first_clause = raw_input.split(" ")[0].strip()
        if len(first_clause) > 120:
            first_clause = first_clause[:117].rstrip() + "..."
        return first_clause

    def _extract_candidate_phrases(self, raw_input: str) -> list[str]:
        if not raw_input:
            return []

        lines = [line.strip() for line in raw_input.splitlines() if line.strip()]
        bullet_lines = [line for line in lines if re.match(r"^(?:[-*•]|\d+[.)])\s+", line)]
        if bullet_lines:
            return [re.sub(r"^(?:[-*•]|\d+[.)])\s+", "", line) for line in bullet_lines]

        clauses = re.split(r"(?<=[.!?;])\s+|\n+", raw_input)
        phrases = [clause.strip() for clause in clauses if clause.strip()]
        if len(phrases) <= 1:
            return [phrase.strip() for phrase in re.split(r"\s+and\s+|\s+then\s+", raw_input) if phrase.strip()]
        return phrases

    def _phrase_to_title(self, phrase: str) -> str:
        phrase = re.sub(r"^(?:to|then|and|also)\s+", "", phrase.strip(), flags=re.IGNORECASE)
        phrase = phrase.strip(" -•\t")
        phrase = phrase.rstrip(".;: ")
        phrase = re.sub(r"\s+", " ", phrase)
        if not phrase:
            return ""
        if len(phrase) > 72:
            phrase = phrase[:69].rstrip() + "..."
        return self._shorten_task_title(phrase)

    def _build_description(self, phrase: str) -> str:
        cleaned = re.sub(r"\s+", " ", phrase.strip(" -•\t"))
        if not cleaned:
            return ""
        if len(cleaned) > 120:
            cleaned = cleaned[:117].rstrip() + "..."
        return f"Derived from: {cleaned}"

    def _fallback_tasks(self, goal_summary: str) -> list[PlanningTaskDraft]:
        goal_label = goal_summary if goal_summary else "this goal"
        return [
            PlanningTaskDraft(
                title=self._shorten_task_title(f"Define the outcome for {self._quoted(goal_label)}"),
                description="Clarify what finished looks like.",
                rationale="Fallback draft",
            ),
            PlanningTaskDraft(
                title=self._shorten_task_title(
                    f"Break {self._quoted(goal_label)} into one independent next step"
                ),
                description="Keep the first move small and meaningful.",
                rationale="Fallback draft",
            ),
            PlanningTaskDraft(
                title=self._shorten_task_title("List constraints, dependencies, and open questions"),
                description="Surface anything that can block the plan.",
                rationale="Fallback draft",
            ),
        ]

    def _quoted(self, text: str) -> str:
        compact = text.strip()
        if len(compact) > 36:
            compact = compact[:33].rstrip() + "..."
        return f"\"{compact}\""

    def _shorten_task_title(self, title: str) -> str:
        words = [word.strip(" ,;:.!?()[]{}") for word in title.split()]
        words = [word for word in words if word]
        if not words:
            return "Task"
        shortened = " ".join(words[:3])
        return shortened[0].upper() + shortened[1:] if len(shortened) > 1 else shortened.upper()

    def _summarize_project_description(self, goal_summary: str, tasks: list[PlanningTaskDraft]) -> str:
        if not tasks:
            return f"Plan for {goal_summary}".strip()

        first_titles = [task.title for task in tasks[:2] if task.title.strip()]
        if not first_titles:
            return f"Plan for {goal_summary}".strip()

        if len(first_titles) == 1:
            description = f"Focuses on {first_titles[0].lower()}."
        else:
            description = f"Focuses on {first_titles[0].lower()} and {first_titles[1].lower()}."

        if len(description) > 120:
            description = description[:117].rstrip() + "..."
        return description

    def _clarifying_question(self, raw_input: str, tasks: list[PlanningTaskDraft]) -> str | None:
        if not raw_input:
            return "What should this planner work on?"

        word_count = len(raw_input.split())
        if word_count < 8:
            return "What concrete outcome should this plan produce?"

        if len(tasks) == 1:
            return "What is the first independent step you want to preserve?"

        if len(tasks) >= 3 and tasks[0].rationale == "Fallback draft":
            return "What detail should the draft separate out first?"

        return None


class GeminiPlanningEngine:
    def __init__(self, client: GeminiClient) -> None:
        self._client = client
        self._schema = {
            "type": "object",
            "additionalProperties": False,
            "required": ["goal_summary", "project_description", "tentative_tasks", "clarification_question"],
            "properties": {
                "goal_summary": {"type": "string"},
                "project_description": {"type": "string"},
                "tentative_tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["title", "description", "rationale"],
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "rationale": {"type": "string"},
                        },
                    },
                },
                "clarification_question": {"type": "string"},
            },
        }

    def draft(self, raw_input: str) -> PlanningDraftResult:
        payload = self._client.generate_json(
            system_instruction=self._system_prompt(),
            user_input=raw_input,
            schema_name="planning_draft",
            schema=self._schema,
        )
        return self._parse_payload(payload, raw_input)

    def _system_prompt(self) -> str:
        return (
            "You are Marshal's planning assistant.\n"
            "Turn the user's raw goal into a tentative list of meaningful, partially independent tasks.\n"
            "Do not write final commitments. Draft only.\n"
            "Keep each task concrete enough to move the goal forward.\n"
            "Keep each task title to three words or fewer.\n"
            "Prefer 3 to 7 tasks unless the goal is very small.\n"
            "If the input is vague, return a short clarification_question.\n"
            "Return JSON that matches the schema exactly."
        )

    def _parse_payload(self, payload: dict[str, object], raw_input: str) -> PlanningDraftResult:
        goal_summary_value = payload.get("goal_summary")
        goal_summary = (
            goal_summary_value.strip()
            if isinstance(goal_summary_value, str) and goal_summary_value.strip()
            else raw_input.strip() or "Untitled goal"
        )
        raw_tasks = payload.get("tentative_tasks") or []
        tentative_tasks: list[PlanningTaskDraft] = []
        if isinstance(raw_tasks, list):
            for item in raw_tasks:
                if not isinstance(item, dict):
                    continue
                title = str(item.get("title") or "").strip()
                if not title:
                    continue
                tentative_tasks.append(
                    PlanningTaskDraft(
                        title=RuleBasedPlanningEngine()._shorten_task_title(title),
                        description=str(item.get("description") or "").strip(),
                        rationale=str(item.get("rationale") or "").strip(),
                    )
                )

        clarification_value = payload.get("clarification_question")
        clarification_question = (
            clarification_value.strip()
            if isinstance(clarification_value, str) and clarification_value.strip()
            else ""
        )
        if not tentative_tasks:
            tentative_tasks = RuleBasedPlanningEngine()._fallback_tasks(goal_summary)
        return PlanningDraftResult(
            goal_summary=goal_summary,
            project_description=self._project_description(payload, goal_summary, tentative_tasks),
            tentative_tasks=tentative_tasks,
            clarification_question=clarification_question or None,
        )

    def _project_description(
        self,
        payload: dict[str, object],
        goal_summary: str,
        tentative_tasks: list[PlanningTaskDraft],
    ) -> str:
        value = payload.get("project_description")
        if isinstance(value, str) and value.strip():
            description = value.strip()
        else:
            description = RuleBasedPlanningEngine()._summarize_project_description(goal_summary, tentative_tasks)
        if len(description) > 120:
            description = description[:117].rstrip() + "..."
        return description


OpenAIPlanningEngine = GeminiPlanningEngine


class PlanningService:
    def __init__(self, engine: PlanningEngine | None = None) -> None:
        self._engine = engine or self._default_engine()

    def _default_engine(self) -> PlanningEngine:
        client = GeminiClient.from_env()
        if client is not None:
            return GeminiPlanningEngine(client)
        return RuleBasedPlanningEngine()

    def create_session(self, raw_input: str) -> PlanningSession:
        result = self._draft(raw_input)
        phase = PlanningPhase.REVIEW
        if result.clarification_question is not None:
            phase = PlanningPhase.DRAFT

        session = PlanningSession(
            raw_input=raw_input.strip(),
            goal_summary=result.goal_summary,
            project_description=result.project_description,
            tentative_tasks=result.tentative_tasks,
            clarification_question=result.clarification_question,
            phase=phase,
        )
        session.transcript.extend(
            [
                f"User:\n{session.raw_input}",
                f"Assistant:\n{self.render_tentative_draft_text(session)}",
            ]
        )
        return session

    def revise_session(self, session: PlanningSession, feedback: str) -> PlanningSession:
        cleaned_feedback = feedback.strip()
        combined_input = session.raw_input
        if cleaned_feedback:
            combined_input = f"{session.raw_input}\n\nUser clarification:\n{cleaned_feedback}"

        result = self._draft(combined_input)
        revised_session = PlanningSession(
            raw_input=session.raw_input,
            goal_summary=result.goal_summary,
            project_description=result.project_description,
            tentative_tasks=result.tentative_tasks,
            clarification_question=result.clarification_question,
            phase=PlanningPhase.REVIEW if result.clarification_question is None else PlanningPhase.DRAFT,
            revision_count=session.revision_count + 1,
            transcript=list(session.transcript),
        )
        if cleaned_feedback:
            revised_session.transcript.extend(
                [
                    f"User clarification:\n{cleaned_feedback}",
                    f"Assistant revision:\n{self.render_tentative_draft_text(revised_session)}",
                ]
            )
        else:
            revised_session.transcript.append(
                f"Assistant revision:\n{self.render_tentative_draft_text(revised_session)}"
            )
        return revised_session

    def _draft(self, raw_input: str) -> PlanningDraftResult:
        try:
            return self._engine.draft(raw_input)
        except Exception:
            if isinstance(self._engine, RuleBasedPlanningEngine):
                raise
            return RuleBasedPlanningEngine().draft(raw_input)

    def approve_session(self, session: PlanningSession) -> PlanningSession:
        structured_tasks = [replace(task) for task in session.tentative_tasks]
        approved_session = replace(
            session,
            structured_tasks=structured_tasks,
            phase=PlanningPhase.APPROVED,
            transcript=list(session.transcript),
        )
        approved_session.transcript.append(
            f"Assistant:\n{self.render_structured_preview_text(approved_session)}"
        )
        return approved_session

    def materialize_session(
        self,
        session: PlanningSession,
        project_service: ProjectService,
        task_service: TaskService,
    ) -> Project:
        approved_session = session
        if approved_session.phase != PlanningPhase.APPROVED:
            approved_session = self.approve_session(approved_session)

        project_title = approved_session.goal_summary.strip() or approved_session.raw_input.strip()
        if not project_title:
            project_title = "Untitled goal"
        project_title = RuleBasedPlanningEngine()._shorten_task_title(project_title)
        project = project_service.create_project(project_title, approved_session.project_description.strip())

        tasks = approved_session.structured_tasks or approved_session.tentative_tasks
        for task in tasks:
            task_service.create_task_for_project(
                project.id,
                RuleBasedPlanningEngine()._shorten_task_title(task.title),
                self._task_comments(task),
            )
        return project

    def render_tentative_draft_text(self, session: PlanningSession) -> str:
        lines = [f"Goal: {session.goal_summary}", "", "Tentative tasks:"]
        if not session.tentative_tasks:
            lines.append("  1. Add more detail so a draft can be generated.")
        else:
            for index, task in enumerate(session.tentative_tasks, start=1):
                lines.append(f"  {index}. {task.title}")
                if task.description:
                    lines.append(f"     {task.description}")
        if session.clarification_question:
            lines.extend(["", f"Clarification: {session.clarification_question}"])
        return "\n".join(lines).strip()

    def render_structured_preview_text(self, session: PlanningSession) -> str:
        if not session.structured_tasks:
            return ""
        lines = ["Structured output:", ""]
        for index, task in enumerate(session.structured_tasks, start=1):
            lines.append(f"{index}. {task.title}")
            if task.description:
                lines.append(f"   details: {task.description}")
            if task.rationale:
                lines.append(f"   source: {task.rationale}")
        return "\n".join(lines).strip()

    def render_transcript_text(self, session: PlanningSession) -> str:
        return "\n\n".join(session.transcript).strip()

    def _task_comments(self, task: PlanningTaskDraft) -> str:
        details: list[str] = []
        if task.description.strip():
            details.append(task.description.strip())
        if task.rationale.strip():
            details.append(f"Source: {task.rationale.strip()}")
        return "\n".join(details)
