import json

from app.art import vocab

JSON_ONLY_SYSTEM = (
    "You are an award-winning children's picture-book author and art director. "
    "You always reply with exactly one valid JSON object and nothing else: no markdown fences, no commentary."
)


def _options(values):
    return " | ".join(f'"{value}"' for value in values)


def story_prompt(user_prompt):
    return (
        "Create a five-page picture book outline for children aged 3 to 7 based on this request:\n"
        f'"""{user_prompt}"""\n\n'
        "Unless the request says otherwise, the story is about a young, brave child who discovers a hidden, magical garden. "
        "The request may add details such as the hero's name or traits; honour them.\n\n"
        "The five pages follow these beats in order:\n"
        "1. Meet the hero and their ordinary world, with a first spark of bravery.\n"
        "2. The hero follows a clue and finds the hidden entrance.\n"
        "3. The hero steps inside and discovers the magical garden.\n"
        "4. A gentle challenge or magical moment where bravery and kindness matter.\n"
        "5. A warm, happy resolution.\n\n"
        "Return JSON with exactly this shape:\n"
        '{"title": "...", "hero_name": "...", "hero_summary": "...", '
        '"pages": [{"page": 1, "beat": "...", "summary": "..."}, ... exactly 5 items]}\n\n'
        "Rules: the title has at most 7 words. hero_name is one first name only. "
        "hero_summary is one sentence describing who the hero is, including whether they are a girl or a boy. "
        "Each page summary is one sentence. Nothing scary, violent or sad."
    )


def character_prompt(story):
    return (
        "Design the single main character of this picture book. The same character is drawn on every page by code, "
        "so you must choose from the fixed options below.\n\n"
        f"Story title: {story.title}\n"
        f"Hero name: {story.hero_name}\n"
        f"Hero summary: {story.hero_summary}\n\n"
        "Return JSON with exactly this shape:\n"
        "{\n"
        f'  "name": "{story.hero_name}",\n'
        '  "age": a number from 5 to 9,\n'
        f"  \"skin_tone\": {_options(vocab.SKIN_TONES)},\n"
        f"  \"hair_color\": {_options(vocab.HAIR_COLORS)},\n"
        f"  \"hair_style\": {_options(vocab.HAIR_STYLES)},\n"
        f"  \"outfit\": {_options(vocab.OUTFITS)},\n"
        f"  \"outfit_color\": {_options(vocab.OUTFIT_COLORS)},\n"
        f"  \"accent_color\": {_options(vocab.OUTFIT_COLORS)} (must differ from outfit_color),\n"
        f"  \"signature_item\": {_options(vocab.SIGNATURE_ITEMS)},\n"
        '  "personality": ["three", "short", "words"]\n'
        "}\n\n"
        "Use only the listed values. Pick a look that fits the hero in the summary: "
        '"tunic" suits a boy or an adventurer, "dress" suits a girl, and the signature item should feel brave and memorable.'
    )


def scenes_prompt(story, character, feedback):
    outline = json.dumps(story.model_dump(), ensure_ascii=False)
    text = (
        "Write the final text and the illustration plan for each of the five pages of this picture book.\n\n"
        f"Story outline: {outline}\n"
        f"Hero: {character.name}, who always wears or carries a {character.signature_item.replace('_', ' ')}.\n\n"
        "For every page return these fields:\n"
        f'- "text": 2 or 3 short, rhythmic sentences of 25 to 45 words in simple words for ages 3 to 7, past tense, mentioning {character.name} by name on most pages. The text must match what the picture shows.\n'
        f"- \"setting\": {_options(vocab.SETTINGS)}\n"
        "  (meadow = open grass with a path, forest = tall friendly trees, wall = an old stone garden wall with a hidden arched door, "
        "garden = lush hedges with a flower arch, glade = a glowing magical tree)\n"
        f"- \"time_of_day\": {_options(vocab.TIMES_OF_DAY)}\n"
        f"- \"elements\": 3 to 6 values from {_options(vocab.ELEMENTS)}\n"
        f"- \"hero_pose\": {_options(vocab.POSES)}\n"
        f"- \"expression\": {_options(vocab.EXPRESSIONS)}\n"
        '- "hero_x": a number from 0.2 to 0.8 (where the hero stands, left to right)\n\n'
        "Visual guidance: page 1 uses a meadow or forest; page 2 uses the wall where the hidden door is found; "
        "page 3 uses a garden and reveals its magic; page 4 uses a glade or garden at its most magical; page 5 is a warm happy ending. "
        "Use at least three different settings and at least three different hero poses across the book.\n\n"
        "Return JSON with exactly this shape:\n"
        '{"scenes": [{"page": 1, "text": "...", "setting": "...", "time_of_day": "...", "elements": ["..."], '
        '"hero_pose": "...", "expression": "...", "hero_x": 0.3}, ... exactly 5 items]}'
    )
    if feedback:
        text += "\n\nYour previous attempt had these problems. Fix all of them:\n" + "\n".join(f"- {item}" for item in feedback)
    return text
