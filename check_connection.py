import sys

from app.config import get_settings
from app.llm import LLMError, chat_text


def main():
    settings = get_settings()
    print(f"Base URL: {settings.airouter_base_url}")
    print(f"Model:    {settings.llm_model}")
    try:
        reply = chat_text([{"role": "user", "content": "Reply with the single word: ready"}])
    except LLMError as exc:
        print(f"Configuration problem: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"Request failed: {exc.__class__.__name__}: {exc}")
        sys.exit(1)
    print(f"Reply:    {reply.strip()}")
    print("Connection OK")


if __name__ == "__main__":
    main()
