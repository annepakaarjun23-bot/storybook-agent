from typing import List

from pydantic import BaseModel, Field, field_validator, model_validator

from app.art import vocab

PAGE_COUNT = 5

SYNONYMS = {
    "skin_tone": {"medium": "tan", "olive": "tan", "dark": "deep", "pale": "light", "beige": "fair", "peach": "fair", "caramel": "brown"},
    "hair_color": {"blond": "blonde", "yellow": "blonde", "gold": "blonde", "golden": "blonde", "ginger": "red", "orange": "red", "dark": "black", "gray": "silver", "grey": "silver", "white": "silver", "chestnut": "brown"},
    "hair_style": {"pigtail": "pigtails", "braids": "pigtails", "buns": "bun", "ponytails": "ponytail", "curls": "curly", "afro": "curly", "bob": "short", "pixie": "short"},
    "outfit": {"skirt": "dress", "overalls": "tunic", "shirt": "tunic", "shorts": "tunic", "pants": "tunic"},
    "signature_item": {"scarves": "scarf", "explorer_hat": "hat", "straw_hat": "hat", "satchel": "backpack", "bag": "backpack", "flowers": "flower_crown", "crown": "flower_crown", "flower": "flower_crown", "cloak": "cape"},
    "setting": {"garden_interior": "garden", "hidden_garden": "garden", "magical_garden": "garden", "gate": "wall", "door": "wall", "stone_wall": "wall", "garden_wall": "wall", "woods": "forest", "field": "meadow", "clearing": "glade", "magic_tree": "glade", "tree": "glade"},
    "time_of_day": {"sunset": "dusk", "evening": "dusk", "morning": "day", "sunrise": "day", "afternoon": "day", "twilight": "dusk", "magical": "magic", "midday": "day", "noon": "day"},
    "hero_pose": {"stand": "standing", "walk": "walking", "reach": "reaching", "point": "pointing", "wave": "waving", "jump": "jumping", "run": "walking", "running": "walking", "amazed": "wonder"},
    "expression": {"excited": "joyful", "amazed": "surprised", "brave": "determined", "wonder": "surprised", "smiling": "happy", "curiosity": "curious", "delighted": "joyful", "awe": "surprised", "smile": "happy", "joy": "joyful"},
    "element": {"tree": "trees", "flower": "flowers", "mushroom": "mushrooms", "butterfly": "butterflies", "firefly": "fireflies", "star": "stars", "sparkle": "sparkles", "lantern": "lanterns", "bush": "bushes", "vine": "vines", "gate": "door", "fairy_lights": "lanterns"},
}


def _normalize(value):
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def _choice(value, allowed, default, kind):
    normalized = _normalize(value)
    normalized = SYNONYMS.get(kind, {}).get(normalized, normalized)
    return normalized if normalized in allowed else default


CHARACTER_CHOICES = {
    "skin_tone": (list(vocab.SKIN_TONES), "tan"),
    "hair_color": (list(vocab.HAIR_COLORS), "brown"),
    "hair_style": (vocab.HAIR_STYLES, "pigtails"),
    "outfit": (vocab.OUTFITS, "dress"),
    "outfit_color": (list(vocab.OUTFIT_COLORS), "red"),
    "accent_color": (list(vocab.OUTFIT_COLORS), "yellow"),
    "signature_item": (vocab.SIGNATURE_ITEMS, "scarf"),
}


class PageOutline(BaseModel):
    page: int = 0
    beat: str = ""
    summary: str = ""


class StoryOutline(BaseModel):
    title: str = Field(min_length=1)
    hero_name: str = Field(min_length=1)
    hero_summary: str = ""
    pages: List[PageOutline]

    @field_validator("title", "hero_name", "hero_summary", mode="before")
    @classmethod
    def strip_text(cls, value):
        return "" if value is None else str(value).strip()

    @field_validator("hero_name", mode="after")
    @classmethod
    def first_name_only(cls, value):
        return value.split()[0] if value.split() else value

    @field_validator("pages", mode="after")
    @classmethod
    def exactly_five(cls, value):
        if len(value) != PAGE_COUNT:
            raise ValueError(f"pages must contain exactly {PAGE_COUNT} items, got {len(value)}")
        return value


class CharacterDesign(BaseModel):
    name: str = Field(min_length=1)
    age: int = 7
    skin_tone: str = "tan"
    hair_color: str = "brown"
    hair_style: str = "pigtails"
    outfit: str = "dress"
    outfit_color: str = "red"
    accent_color: str = "yellow"
    signature_item: str = "scarf"
    personality: List[str] = []

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, value):
        return "" if value is None else str(value).strip()

    @field_validator("age", mode="before")
    @classmethod
    def coerce_age(cls, value):
        try:
            return min(max(int(float(value)), 3), 12)
        except (TypeError, ValueError):
            return 7

    @field_validator(*CHARACTER_CHOICES.keys(), mode="before")
    @classmethod
    def coerce_choice(cls, value, info):
        allowed, default = CHARACTER_CHOICES[info.field_name]
        return _choice(value, allowed, default, info.field_name)

    @field_validator("personality", mode="before")
    @classmethod
    def coerce_personality(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            value = [value]
        return [str(item).strip() for item in value if str(item).strip()][:5]

    @model_validator(mode="after")
    def distinct_colors(self):
        if self.accent_color == self.outfit_color:
            options = list(vocab.OUTFIT_COLORS)
            index = options.index(self.outfit_color)
            self.accent_color = options[(index + 3) % len(options)]
        return self


class ScenePlan(BaseModel):
    page: int = 0
    text: str = Field(min_length=1)
    setting: str = "meadow"
    time_of_day: str = "day"
    elements: List[str] = []
    hero_pose: str = "standing"
    expression: str = "happy"
    hero_x: float = 0.4

    @field_validator("text", mode="before")
    @classmethod
    def clean_text(cls, value):
        return "" if value is None else " ".join(str(value).split())

    @field_validator("setting", mode="before")
    @classmethod
    def coerce_setting(cls, value):
        return _choice(value, vocab.SETTINGS, "meadow", "setting")

    @field_validator("time_of_day", mode="before")
    @classmethod
    def coerce_time(cls, value):
        return _choice(value, vocab.TIMES_OF_DAY, "day", "time_of_day")

    @field_validator("hero_pose", mode="before")
    @classmethod
    def coerce_pose(cls, value):
        return _choice(value, vocab.POSES, "standing", "hero_pose")

    @field_validator("expression", mode="before")
    @classmethod
    def coerce_expression(cls, value):
        return _choice(value, vocab.EXPRESSIONS, "happy", "expression")

    @field_validator("elements", mode="before")
    @classmethod
    def coerce_elements(cls, value):
        if value is None:
            value = []
        if isinstance(value, str):
            value = [part for part in value.replace(";", ",").split(",")]
        cleaned = []
        for item in value:
            name = _choice(item, vocab.ELEMENTS, "", "element")
            if name and name not in cleaned:
                cleaned.append(name)
        return cleaned[:6] or ["flowers"]

    @field_validator("hero_x", mode="before")
    @classmethod
    def coerce_hero_x(cls, value):
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0.4
        return min(max(number, 0.2), 0.8)


class ScenePlanSet(BaseModel):
    scenes: List[ScenePlan]

    @field_validator("scenes", mode="after")
    @classmethod
    def exactly_five(cls, value):
        if len(value) != PAGE_COUNT:
            raise ValueError(f"scenes must contain exactly {PAGE_COUNT} items, got {len(value)}")
        return value


class BookRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=1000)
