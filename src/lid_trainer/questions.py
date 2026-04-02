"""Question bank loader and manager for the Leben in Deutschland test."""

import json
import random
from dataclasses import dataclass
from pathlib import Path

STATES = [
    "Baden-Württemberg",
    "Bayern",
    "Berlin",
    "Brandenburg",
    "Bremen",
    "Hamburg",
    "Hessen",
    "Mecklenburg-Vorpommern",
    "Niedersachsen",
    "Nordrhein-Westfalen",
    "Rheinland-Pfalz",
    "Saarland",
    "Sachsen",
    "Sachsen-Anhalt",
    "Schleswig-Holstein",
    "Thüringen",
]


@dataclass
class Question:
    """A single test question with options and correct answer."""

    id: int
    question: str
    options: list[str]
    correct_answer: int
    question_type: str  # "general" or "state"
    state: str | None
    has_image: bool = False
    image: str | None = None
    question_en: str = ""
    options_en: list[str] | None = None

    def is_correct(self, answer_index: int) -> bool:
        """Check if the given answer index is correct."""
        return answer_index == self.correct_answer

    @property
    def correct_text(self) -> str:
        """Return the text of the correct answer."""
        return self.options[self.correct_answer]


class QuestionBank:
    """Manages the full question bank with filtering and selection."""

    def __init__(self, questions: list[Question] | None = None) -> None:
        """Initialize with questions, or load from bundled data."""
        if questions is not None:
            self._questions = questions
        else:
            self._questions = self._load_bundled()

    @staticmethod
    def _load_bundled() -> list[Question]:
        """Load questions from the bundled JSON data file."""
        data_path = Path(__file__).parent / "data" / "questions.json"
        with open(data_path, encoding="utf-8") as f:
            raw = json.load(f)
        return [
            Question(
                id=q["id"],
                question=q["question"],
                options=q["options"],
                correct_answer=q["correct_answer"],
                question_type=q["type"],
                state=q.get("state"),
                has_image=q.get("has_image", False),
                image=q.get("image"),
                question_en=q.get("question_en", ""),
                options_en=q.get("options_en"),
            )
            for q in raw
        ]

    @property
    def all_questions(self) -> list[Question]:
        """Return all questions."""
        return self._questions

    def general_questions(self) -> list[Question]:
        """Return only general (Teil I) questions."""
        return [q for q in self._questions if q.question_type == "general"]

    def state_questions(self, state: str) -> list[Question]:
        """Return questions for a specific Bundesland."""
        return [q for q in self._questions if q.state == state]

    def exam_simulation(self, state: str) -> list[Question]:
        """Generate a simulated exam: 30 general + 3 state questions."""
        general = self.general_questions()
        state_qs = self.state_questions(state)
        selected = random.sample(general, min(30, len(general)))
        selected += random.sample(state_qs, min(3, len(state_qs)))
        random.shuffle(selected)
        return selected
