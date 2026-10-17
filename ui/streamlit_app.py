import base64
import html
import os
import time

import requests
import streamlit as st

DEFAULT_API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
DEFAULT_PROMPT = (
    "Create a five-page children's book story about a young, brave character "
    "discovering a hidden, magical garden."
)
POLL_SECONDS = 1.2
TIMEOUT_SECONDS = 900

st.set_page_config(page_title="Storybook Agent", page_icon="📖", layout="wide")

st.markdown(
    """
    <style>
    .block-container {max-width: 1100px; padding-top: 2rem;}
    .story-card {background: #fff8ec; border: 2px solid #e3c99a; border-radius: 18px; padding: 14px 14px 6px 14px; margin-bottom: 18px;}
    .story-card img {width: 100%; border-radius: 12px; display: block;}
    .story-text {font-family: Georgia, 'Times New Roman', serif; font-size: 1.05rem; color: #4a3b2f; padding: 10px 6px 8px 6px; line-height: 1.5;}
    .page-tag {font-size: 0.8rem; font-weight: 700; color: #c9822b; letter-spacing: 0.08em; text-transform: uppercase;}
    </style>
    """,
    unsafe_allow_html=True,
)

for key, value in {"job_id": None, "result": None, "error": None}.items():
    st.session_state.setdefault(key, value)

with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("API URL", value=DEFAULT_API_URL).rstrip("/")
    if st.button("Check API connection"):
        try:
            info = requests.get(f"{api_url}/health", timeout=5).json()
            st.success(f"Connected. Model: {info['model']}")
            if info.get("demo_mode"):
                st.info("Demo mode is on: no AI credits are used.")
            elif not info.get("api_key_configured"):
                st.warning("The API has no AIROUTER_API_KEY configured.")
        except Exception as exc:
            st.error(f"Cannot reach the API: {exc}")
    if st.button("Start over"):
        st.session_state.update({"job_id": None, "result": None, "error": None})
        st.rerun()


def svg_html(svg_text):
    encoded = base64.b64encode(svg_text.encode("utf-8")).decode("ascii")
    return f'<img src="data:image/svg+xml;base64,{encoded}" alt="illustration"/>'


def fetch_result(job, base_url):
    job_id = job["job_id"]
    pdf = requests.get(f"{base_url}/books/{job_id}/pdf", timeout=60)
    pdf.raise_for_status()
    svgs = []
    for page in range(0, 6):
        response = requests.get(f"{base_url}/books/{job_id}/pages/{page}", timeout=60)
        response.raise_for_status()
        svgs.append(response.text)
    return {"job": job, "pdf": pdf.content, "svgs": svgs}


def poll_job(job_id, base_url):
    bar = st.progress(0, text="Starting")
    started = time.time()
    while True:
        try:
            job = requests.get(f"{base_url}/books/{job_id}", timeout=15).json()
        except Exception as exc:
            return None, f"Lost connection to the API: {exc}"
        bar.progress(min(int(job.get("progress", 0)), 100) / 100, text=job.get("message", "Working"))
        if job["status"] == "completed":
            return job, None
        if job["status"] == "failed":
            return None, job.get("error") or "The job failed."
        if time.time() - started > TIMEOUT_SECONDS:
            return None, "Timed out while waiting for the story."
        time.sleep(POLL_SECONDS)


def render_result(result):
    job = result["job"]
    st.success(f"“{job['title']}” is ready.")
    st.download_button(
        "Download PDF",
        data=result["pdf"],
        file_name=f"{job['title'].replace(' ', '_')}.pdf",
        mime="application/pdf",
        type="primary",
    )
    st.markdown(f'<div class="story-card">{svg_html(result["svgs"][0])}</div>', unsafe_allow_html=True)
    columns = st.columns(2)
    for index, page in enumerate(job["pages"], start=1):
        with columns[(index - 1) % 2]:
            st.markdown(
                f'<div class="story-card">{svg_html(result["svgs"][index])}'
                f'<div class="story-text"><div class="page-tag">Page {index}</div>{html.escape(page["text"])}</div></div>',
                unsafe_allow_html=True,
            )


st.title("📖 Storybook Agent")
st.caption("Turn one idea into an illustrated five-page picture book with a consistent hero, ready as a PDF.")

prompt = st.text_area("Your story idea", value=DEFAULT_PROMPT, height=110, max_chars=1000)

if st.button("Create my storybook", type="primary", disabled=len(prompt.strip()) < 3):
    st.session_state.update({"result": None, "error": None})
    try:
        response = requests.post(f"{api_url}/books", json={"prompt": prompt.strip()}, timeout=15)
        response.raise_for_status()
        st.session_state["job_id"] = response.json()["job_id"]
    except Exception as exc:
        st.session_state["job_id"] = None
        st.session_state["error"] = f"Could not start the job. Is the API running at {api_url}? ({exc})"

if st.session_state["job_id"] and not st.session_state["result"] and not st.session_state["error"]:
    finished, problem = poll_job(st.session_state["job_id"], api_url)
    if problem:
        st.session_state["error"] = problem
    else:
        try:
            st.session_state["result"] = fetch_result(finished, api_url)
        except Exception as exc:
            st.session_state["error"] = f"The story finished but the files could not be loaded: {exc}"

if st.session_state["error"]:
    st.error(st.session_state["error"])

if st.session_state["result"]:
    render_result(st.session_state["result"])
