from .reasoning import ProblemFrame, decompose_problem, format_problem_frame, candidate_hypotheses
from .evaluation import Review, review_answer, compare_options
from .knowledge_store import KnowledgeStore
from .learning import FeedbackJournal
from .intent import IntentResult, classify_intent
from .context import ContextWindow, build_context_window
from .references import Reference, detect_references
from .ambiguity import AmbiguityReport, analyze_ambiguity
from .comprehension import Comprehension, understand_message
from .learning_v2 import LearningCandidate, LearningPipeline
from .pipeline import CognitivePipeline, CognitiveResult

__all__ = [
    "ProblemFrame", "decompose_problem", "format_problem_frame", "candidate_hypotheses",
    "Review", "review_answer", "compare_options", "KnowledgeStore", "FeedbackJournal",
    "IntentResult", "classify_intent", "ContextWindow", "build_context_window",
    "Reference", "detect_references", "AmbiguityReport", "analyze_ambiguity",
    "Comprehension", "understand_message", "LearningCandidate", "LearningPipeline",
    "CognitivePipeline", "CognitiveResult", "KenzieCognitiveAdapter", "PreparedTurn",
]

from .integration import KenzieCognitiveAdapter, PreparedTurn
