from types import SimpleNamespace

import pytest

from app.graph.quality import evaluate_scenes
from app.jsonutil import extract_json


def scene(text, setting="meadow", pose="standing"):
    return SimpleNamespace(text=text, setting=setting, hero_pose=pose)


GOOD_TEXT = "Mia walked along the sunny path with a big brave smile and a happy skip in her step today."


def test_extract_json_plain():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_fenced_with_chatter():
    assert extract_json('Sure!\n```json\n{"a": [1, 2]}\n```\nEnjoy') == {"a": [1, 2]}


def test_extract_json_rejects_garbage():
    with pytest.raises(ValueError):
        extract_json("no braces here")


def test_quality_accepts_good_scenes():
    scenes = [
        scene(GOOD_TEXT, "meadow", "walking"),
        scene(GOOD_TEXT, "wall", "reaching"),
        scene(GOOD_TEXT, "garden", "wonder"),
        scene(GOOD_TEXT, "glade", "jumping"),
        scene(GOOD_TEXT, "garden", "waving"),
    ]
    assert evaluate_scenes(scenes, "Mia") == []


def test_quality_flags_problems():
    scenes = [scene("Too short.") for _ in range(5)]
    problems = evaluate_scenes(scenes, "Mia")
    assert any("words" in item for item in problems)
    assert any("settings" in item for item in problems)
    assert any("poses" in item for item in problems)
    assert any("magical garden" in item for item in problems)
    assert any("by name" in item for item in problems)
