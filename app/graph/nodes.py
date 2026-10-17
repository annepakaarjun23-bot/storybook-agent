import json

from app.config import get_settings
from app.graph.quality import MAX_SCENE_ATTEMPTS, evaluate_scenes
from app.llm import generate_structured
from app.prompts import templates
from app.schemas import CharacterDesign, ScenePlanSet, StoryOutline
from app.services.illustrator import build_all_drawings, write_svgs
from app.services.pdf_builder import build_pdf


def job_dir(state):
    path = get_settings().output_dir / state["job_id"]
    path.mkdir(parents=True, exist_ok=True)
    return path


def story_planner(state):
    story = generate_structured(StoryOutline, templates.JSON_ONLY_SYSTEM, templates.story_prompt(state["prompt"]))
    return {"story": story}


def character_designer(state):
    story = state["story"]
    character = generate_structured(CharacterDesign, templates.JSON_ONLY_SYSTEM, templates.character_prompt(story))
    character = character.model_copy(update={"name": story.hero_name})
    return {"character": character}


def scene_planner(state):
    story = state["story"]
    character = state["character"]
    result = generate_structured(
        ScenePlanSet,
        templates.JSON_ONLY_SYSTEM,
        templates.scenes_prompt(story, character, state.get("feedback", [])),
    )
    scenes = [scene.model_copy(update={"page": index}) for index, scene in enumerate(result.scenes, start=1)]
    return {"scenes": scenes, "attempts": state.get("attempts", 0) + 1}


def quality_gate(state):
    problems = evaluate_scenes(state["scenes"], state["character"].name)
    return {"feedback": problems}


def route_after_gate(state):
    if state.get("feedback") and state.get("attempts", 0) < MAX_SCENE_ATTEMPTS:
        return "scene_planner"
    return "page_composer"


def page_composer(state):
    directory = job_dir(state)
    drawings = build_all_drawings(state["character"], state["scenes"])
    svg_paths = write_svgs(drawings, directory)
    snapshot = {
        "prompt": state["prompt"],
        "story": state["story"].model_dump(),
        "character": state["character"].model_dump(),
        "scenes": [scene.model_dump() for scene in state["scenes"]],
    }
    (directory / "story.json").write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"drawings": drawings, "svg_paths": svg_paths}


def pdf_assembler(state):
    directory = job_dir(state)
    pdf_path = build_pdf(
        state["story"].title,
        state["character"],
        state["scenes"],
        directory / "storybook.pdf",
        drawings=state["drawings"],
    )
    return {"pdf_path": pdf_path}
