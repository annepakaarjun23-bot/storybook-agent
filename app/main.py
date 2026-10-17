import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse, Response

from app import jobs
from app.config import get_settings
from app.schemas import BookRequest


@asynccontextmanager
async def lifespan(_app):
    get_settings().output_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Storybook Agent API", version="1.0.0", lifespan=lifespan)


@app.get("/health")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "model": settings.llm_model,
        "demo_mode": settings.demo_mode,
        "api_key_configured": bool(settings.airouter_api_key),
    }


@app.post("/books", status_code=202)
def create_book(request: BookRequest, background_tasks: BackgroundTasks):
    prompt = request.prompt.strip()
    job_id = jobs.create_job(prompt)
    background_tasks.add_task(jobs.run_job, job_id, prompt)
    return {"job_id": job_id, "status": "queued"}


def _require_job(job_id):
    record = jobs.read_job(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return record


@app.get("/books/{job_id}")
def get_book(job_id: str):
    return _require_job(job_id)


@app.get("/books/{job_id}/pdf")
def download_pdf(job_id: str):
    record = _require_job(job_id)
    path = jobs.job_directory(job_id) / "storybook.pdf"
    if record["status"] != "completed" or not path.exists():
        raise HTTPException(status_code=409, detail="The PDF is not ready yet")
    slug = re.sub(r"[^A-Za-z0-9]+", "_", record.get("title") or "storybook").strip("_") or "storybook"
    return FileResponse(Path(path), media_type="application/pdf", filename=f"{slug}.pdf")


@app.get("/books/{job_id}/pages/{page}")
def get_page_svg(job_id: str, page: int):
    _require_job(job_id)
    if page < 0 or page > 5:
        raise HTTPException(status_code=404, detail="Page must be between 0 (cover) and 5")
    name = "cover.svg" if page == 0 else f"page_{page}.svg"
    path = jobs.job_directory(job_id) / name
    if not path.exists():
        raise HTTPException(status_code=409, detail="This page is not ready yet")
    return Response(content=path.read_text(encoding="utf-8"), media_type="image/svg+xml")
