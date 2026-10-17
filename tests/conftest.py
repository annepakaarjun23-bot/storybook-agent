import pytest


@pytest.fixture
def demo_env(monkeypatch, tmp_path):
    from app.config import get_settings

    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path))
    get_settings.cache_clear()
    yield tmp_path
    get_settings.cache_clear()
