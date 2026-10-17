from typing import Any, List, TypedDict

from app.schemas import CharacterDesign, ScenePlan, StoryOutline


class BookState(TypedDict, total=False):
    job_id: str
    prompt: str
    story: StoryOutline
    character: CharacterDesign
    scenes: List[ScenePlan]
    feedback: List[str]
    attempts: int
    drawings: List[Any]
    svg_paths: List[str]
    pdf_path: str
