import time

from fastapi.testclient import TestClient

from app.schemas import CharacterDesign, ScenePlan


def test_schema_coercion():
    character = CharacterDesign.model_validate(
        {"name": " Leo ", "age": "8", "skin_tone": "Olive", "hair_color": "Blond", "hair_style": "Afro",
         "outfit": "shorts", "outfit_color": "red", "accent_color": "red", "signature_item": "Explorer Hat"}
    )
    assert character.name == "Leo"
    assert character.age == 8
    assert character.skin_tone == "tan"
    assert character.hair_color == "blonde"
    assert character.hair_style == "curly"
    assert character.outfit == "tunic"
    assert character.signature_item == "hat"
    assert character.accent_color != character.outfit_color


def test_scene_coercion():
    scene = ScenePlan.model_validate(
        {"text": "  Hello   there  ", "setting": "Hidden Garden", "time_of_day": "sunset",
         "elements": "tree, flower, nonsense", "hero_pose": "jump", "expression": "excited", "hero_x": 5}
    )
    assert scene.text == "Hello there"
    assert scene.setting == "garden"
    assert scene.time_of_day == "dusk"
    assert scene.elements == ["trees", "flowers"]
    assert scene.hero_pose == "jumping"
    assert scene.expression == "joyful"
    assert scene.hero_x == 0.8


def test_full_demo_flow_through_api(demo_env):
    from app.main import app

    with TestClient(app) as client:
        assert client.get("/health").json()["demo_mode"] is True
        created = client.post("/books", json={"prompt": "A brave child finds a hidden garden"})
        assert created.status_code == 202
        job_id = created.json()["job_id"]

        job = {}
        for _ in range(60):
            job = client.get(f"/books/{job_id}").json()
            if job["status"] in ("completed", "failed"):
                break
            time.sleep(0.5)
        assert job["status"] == "completed", job.get("error")
        assert len(job["pages"]) == 5

        pdf = client.get(f"/books/{job_id}/pdf")
        assert pdf.status_code == 200
        assert pdf.content.startswith(b"%PDF")

        for page in range(6):
            svg = client.get(f"/books/{job_id}/pages/{page}")
            assert svg.status_code == 200
            assert b"<svg" in svg.content

        assert client.get("/books/not-a-real-id").status_code == 404
