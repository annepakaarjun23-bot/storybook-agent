import logging
import time
from functools import lru_cache

from app import demo_data
from app.config import get_settings
from app.jsonutil import extract_json

logger = logging.getLogger("storybook.llm")


class LLMError(RuntimeError):
    pass


@lru_cache
def get_client():
    settings = get_settings()
    if not settings.airouter_api_key:
        raise LLMError("AIROUTER_API_KEY is not set. Add it to your .env file.")
    from openai import OpenAI

    return OpenAI(
        api_key=settings.airouter_api_key,
        base_url=settings.airouter_base_url,
        timeout=settings.request_timeout,
        max_retries=2,
    )


def _content_to_text(content):
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("text"):
            parts.append(block["text"])
        elif getattr(block, "text", None):
            parts.append(block.text)
    return "".join(parts)


def chat_text(messages):
    settings = get_settings()
    client = get_client()
    kwargs = {"model": settings.llm_model, "messages": messages}
    if settings.reasoning_effort:
        kwargs["reasoning_effort"] = settings.reasoning_effort
    response = client.chat.completions.create(**kwargs)
    return _content_to_text(response.choices[0].message.content)


def generate_structured(schema, system, user):
    settings = get_settings()
    if settings.demo_mode:
        return schema.model_validate(demo_data.DEMO[schema.__name__])

    base = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    last_error = ""
    attempts = max(settings.llm_max_attempts, 1)
    for attempt in range(1, attempts + 1):
        messages = list(base)
        if last_error:
            messages.append(
                {
                    "role": "user",
                    "content": "Your previous reply was rejected: "
                    + last_error
                    + "\nReply again with one corrected JSON object only.",
                }
            )
        try:
            text = chat_text(messages)
        except LLMError:
            raise
        except Exception as exc:
            last_error = f"the request failed ({exc.__class__.__name__}: {str(exc)[:200]})"
            logger.warning("LLM request failed on attempt %s: %s", attempt, last_error)
            if attempt < attempts:
                time.sleep(2 * attempt)
            continue
        try:
            return schema.model_validate(extract_json(text))
        except ValueError as exc:
            last_error = str(exc)[:500]
            logger.warning("Invalid model output on attempt %s: %s", attempt, last_error)
    raise LLMError(f"The model did not return a usable {schema.__name__} after {attempts} attempts. Last problem: {last_error}")
