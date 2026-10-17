from types import SimpleNamespace

from app.art.scene import SceneSpec
from app.services.illustrator import build_all_drawings, write_svgs
from app.services.pdf_builder import build_pdf, clean_text

CHARACTER = SimpleNamespace(
    name="Mia",
    skin_tone="tan",
    hair_color="brown",
    hair_style="pigtails",
    outfit="dress",
    outfit_color="red",
    accent_color="yellow",
    signature_item="scarf",
)


def make_scenes():
    settings = ["meadow", "wall", "garden", "glade", "garden"]
    poses = ["walking", "reaching", "wonder", "jumping", "waving"]
    scenes = []
    for index in range(5):
        spec = SceneSpec(settings[index], "day", ["flowers", "butterflies"], poses[index], "happy", 0.3)
        spec.text = f"Mia explored page {index + 1} with a brave and happy heart."
        scenes.append(spec)
    return scenes


def test_pdf_has_cover_and_five_pages(tmp_path):
    scenes = make_scenes()
    path = build_pdf("A Test Story", CHARACTER, scenes, tmp_path / "book.pdf")
    data = open(path, "rb").read()
    assert data.startswith(b"%PDF")
    assert data.count(b"/Type /Page\n") + data.count(b"/Type /Page ") >= 6


def test_svgs_written_for_every_page(tmp_path):
    drawings = build_all_drawings(CHARACTER, make_scenes())
    paths = write_svgs(drawings, tmp_path)
    assert len(paths) == 6
    for path in paths:
        assert open(path, encoding="utf-8").read().lstrip().startswith("<?xml")


def test_clean_text_removes_unsupported_characters():
    assert clean_text("Hello \U0001F600 world") == "Hello  world"
    assert "\u201c" in clean_text("\u201cquoted\u201d")
