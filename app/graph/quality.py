MIN_WORDS = 15
MAX_WORDS = 65
MAX_SCENE_ATTEMPTS = 3


def evaluate_scenes(scenes, hero_name):
    problems = []
    if len(scenes) != 5:
        problems.append(f"There must be exactly 5 pages, but {len(scenes)} were returned.")
        return problems
    for index, scene in enumerate(scenes, start=1):
        words = len(scene.text.split())
        if words < MIN_WORDS:
            problems.append(f"Page {index} text has only {words} words; write 25 to 45 words.")
        elif words > MAX_WORDS:
            problems.append(f"Page {index} text has {words} words; shorten it to 25 to 45 words.")
    if len({scene.setting for scene in scenes}) < 3:
        problems.append("Use at least three different settings across the five pages.")
    if len({scene.hero_pose for scene in scenes}) < 3:
        problems.append("Use at least three different hero poses across the five pages.")
    if not any(scene.setting in ("garden", "glade") for scene in scenes):
        problems.append("At least one page must show the magical garden (setting garden or glade).")
    name = hero_name.lower()
    mentions = sum(1 for scene in scenes if name in scene.text.lower())
    if mentions < 3:
        problems.append(f"Mention {hero_name} by name on at least three pages.")
    return problems
