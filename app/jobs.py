import json
import logging
import os
import re
import threading
import uuid
from datetime import datetime, timezone

from app.config import get_settings
from app.graph.quality import MAX_SCENE_ATTEMPTS

logger = logging.getLogger("storybook.jobs")

JOB_ID_PATTERN = re.compile(r"^[a-f0-9]{32}$")
LOCK = threading.Lock()

STEP_INFO = {
    "story_planner": ("Writing the story outline", 15),
    "character_designer": ("Designing the hero", 30),
    "scene_planner": ("Writing the pages and planning the pictures", 55),
    "quality_gate": ("Checking the story", 65),
    "page_composer": ("Drawing the illustrations", 85),
    "pdf_assembler": ("Assembling the PDF", 100),
}
NEXT_STEP = {
    "story_planner": "character_designer",
    "character_designer": "scene_planner",
    "scene_planner": "quality_gate",
    "quality_gate": "page_composer",
    "page_composer": "pdf_assembler",
}


def is_valid_job_id(job_id):
    return bool(JOB_ID_PATTERN.match(job_id or ""))


def job_directory(job_id):
    return get_settings().output_dir / job_id


def _record_path(job_id):
    return job_directory(job_id) / "job.json"


def _now():
    return datetime.now(timezone.utc).isoformat()


def _write(job_id, record):
    path = _record_path(job_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    with LOCK:
        temp.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(temp, path)


def read_job(job_id):
    if not is_valid_job_id(job_id):
        return None
    path = _record_path(job_id)
    with LOCK:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))


def create_job(prompt):
    job_id = uuid.uuid4().hex
    _write(
        job_id,
        {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "message": "Waiting to start",
            "prompt": prompt,
            "title": None,
            "hero_name": None,
            "pages": [],
            "error": None,
            "pdf_ready": False,
            "created_at": _now(),
            "updated_at": _now(),
        },
    )
    return job_id


def _update(job_id, **changes):
    record = read_job(job_id)
    record.update(changes)
    record["updated_at"] = _now()
    _write(job_id, record)
    return record


def run_job(job_id, prompt):
    from app.graph.builder import build_graph

    try:
        _update(job_id, status="running", progress=5, message="Writing the story outline")
        graph = build_graph()
        state = {"job_id": job_id, "prompt": prompt, "feedback": [], "attempts": 0}
        for update in graph.stream(dict(state), stream_mode="updates"):
            for node, output in update.items():
                state.update(output or {})
                label, progress = STEP_INFO[node]
                if node == "quality_gate" and state.get("feedback") and state.get("attempts", 0) < MAX_SCENE_ATTEMPTS:
                    message, progress = "Polishing the pages", 55
                elif node in NEXT_STEP:
                    message = STEP_INFO[NEXT_STEP[node]][0]
                else:
                    message = "Finished"
                changes = {"progress": progress, "message": message}
                if node == "story_planner":
                    changes["title"] = state["story"].title
                    changes["hero_name"] = state["story"].hero_name
                _update(job_id, **changes)
        pages = [{"page": scene.page, "text": scene.text} for scene in state["scenes"]]
        _update(
            job_id,
            status="completed",
            progress=100,
            message="Your storybook is ready",
            title=state["story"].title,
            hero_name=state["character"].name,
            character=state["character"].model_dump(),
            pages=pages,
            pdf_ready=True,
        )
    except Exception as exc:
        logger.exception("Job %s failed", job_id)
        _update(job_id, status="failed", message="Something went wrong", error=str(exc)[:600])
