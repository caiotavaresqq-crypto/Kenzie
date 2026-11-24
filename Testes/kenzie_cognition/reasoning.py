"""Structured reasoning helpers. These tools expose summaries, not private chain-of-thought."""
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class ProblemFrame:
    goal: str
    knowns: List[str]
    unknowns: List[str]
    constraints: List[str]
    subproblems: List[str]


def decompose_problem(goal: str, context: str = "", constraints: List[str] | None = None) -> ProblemFrame:
    """Create a useful problem frame without pretending to solve it automatically."""
    goal = goal.strip()
    constraints = list(constraints or [])
    context_parts = [p.strip() for p in context.splitlines() if p.strip()]
    knowns = context_parts
    unknowns = ["What information is missing?", "What assumptions would need verification?"] if not context_parts else ["Which facts still need verification?"]
    subs = [
        "Restate the target in measurable terms",
        "Separate facts from assumptions",
        "Identify missing information and constraints",
        "Generate candidate approaches",
        "Compare approaches against constraints",
        "Verify the result and explain limitations",
    ]
    return ProblemFrame(goal=goal, knowns=knowns, unknowns=unknowns, constraints=constraints, subproblems=subs)



def format_problem_frame(frame: ProblemFrame) -> str:
    lines = [f"GOAL: {frame.goal}"]
    for label, items in (("KNOWN CONTEXT", frame.knowns), ("UNKNOWN / VERIFY", frame.unknowns), ("CONSTRAINTS", frame.constraints), ("WORK PLAN", frame.subproblems)):
        lines.append(f"\n{label}:")
        lines.extend(f"- {item}" for item in items) if items else lines.append("- (none provided)")
    return "\n".join(lines)



def candidate_hypotheses(question: str, observations: List[str], limit: int = 5) -> dict:
    """Return a hypothesis-generation scaffold; the model fills candidate explanations."""
    return {
        "question": question.strip(),
        "observations": list(observations),
        "candidates_requested": max(1, min(int(limit), 10)),
        "instructions": "List plausible explanations, evidence for/against each, and a next test. Do not treat candidates as facts.",
    }
