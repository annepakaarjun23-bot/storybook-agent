from pathlib import Path

from reportlab.graphics import renderSVG

from app.art.scene import SceneSpec, compose_scene
from app.services.layout import ILL_H, ILL_W, PAGE_H, PAGE_W

COVER_SPEC = SceneSpec(
    setting="garden",
    time_of_day="day",
    elements=["flowers", "butterflies", "sparkles", "trees"],
    hero_pose="waving",
    expression="joyful",
    hero_x=0.45,
)


def build_cover_drawing(character):
    return compose_scene(COVER_SPEC, character, PAGE_W, PAGE_H, seed=4242, hero_scale=0.72)


def build_page_drawing(character, scene, index):
    return compose_scene(scene, character, ILL_W, ILL_H, seed=1000 + index * 37)


def build_all_drawings(character, scenes):
    drawings = [build_cover_drawing(character)]
    for index, scene in enumerate(scenes, start=1):
        drawings.append(build_page_drawing(character, scene, index))
    return drawings


def write_svgs(drawings, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for index, drawing in enumerate(drawings):
        name = "cover.svg" if index == 0 else f"page_{index}.svg"
        path = directory / name
        path.write_text(renderSVG.drawToString(drawing), encoding="utf-8")
        paths.append(str(path))
    return paths
