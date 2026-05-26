import io
import random
import re
from urllib.parse import urlparse

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

AVATAR_SIZE = 256
AVATAR_FONT_SIZE = 128
AVATAR_BACKGROUND_INDIGO = "#4f46e5"
AVATAR_BACKGROUND_TEAL = "#0f766e"
AVATAR_BACKGROUND_SKY = "#0369a1"
AVATAR_BACKGROUND_AMBER = "#b45309"
AVATAR_BACKGROUND_ROSE = "#be123c"
AVATAR_BACKGROUND_SLATE = "#334155"
AVATAR_BACKGROUND_COLORS = (
    AVATAR_BACKGROUND_INDIGO,
    AVATAR_BACKGROUND_TEAL,
    AVATAR_BACKGROUND_SKY,
    AVATAR_BACKGROUND_AMBER,
    AVATAR_BACKGROUND_ROSE,
    AVATAR_BACKGROUND_SLATE,
)
PHONE_PATTERN = r"(8\d{10}|\+7\d{10})"


def normalize_phone(value: str) -> str:
    value = value.strip()
    if value.startswith("8"):
        value = "+7" + value[1:]
    return value


def is_valid_phone(value: str) -> bool:
    return bool(re.fullmatch(PHONE_PATTERN, value))


def is_github_url(value: str) -> bool:
    if not value:
        return True
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and parsed.netloc.lower().endswith("github.com")


def make_avatar(name: str, email: str) -> ContentFile:
    img = Image.new(
        "RGB", (AVATAR_SIZE, AVATAR_SIZE), color=random.choice(AVATAR_BACKGROUND_COLORS)
    )
    draw = ImageDraw.Draw(img)
    letter = (name[:1] or email[:1] or "?").upper()
    try:
        font = ImageFont.truetype("arial.ttf", AVATAR_FONT_SIZE)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter, font=font)
    x = (AVATAR_SIZE - (bbox[2] - bbox[0])) / 2
    y = (AVATAR_SIZE - (bbox[3] - bbox[1])) / 2
    draw.text((x, y), letter, fill="white", font=font)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"avatar_{email}.png")
