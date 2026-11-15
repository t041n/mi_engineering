import re
import unicodedata
from django.utils.text import slugify


FRACTION_MAP = {
    "1/2": "half-inch",
    "1/4": "quarter-inch",
    "3/4": "three-quarter-inch",
    "3/8": "three-eighth-inch",
    "5/8": "five-eighth-inch",
    "1/8": "one-eighth-inch",
    "5/16": "five-sixteenth-inch",
    "7/16": "seven-sixteenth-inch",
    "9/16": "nine-sixteenth-inch",
    "1/16": "one-sixteenth-inch",
    "3/16": "three-sixteenth-inch",
    "1/32": "one-thirty-second-inch",
    "7/8": "seven-eighth-inch",
}

SYMBOL_REPLACEMENTS = [
    # Multiplications and dimensional bys (e.g. M12 x 1.75 -> m12-x-1-75)
    (re.compile(r"(\d+)\s*[xX×]\s*(\d+)"), r"\1-x-\2"),
    # Diameter symbol (⌀, ø, Ø)
    (re.compile(r"[⌀øØ]"), "dia-"),
    # Pitch or thread markings (e.g., M12x1.5 -> m12-x-1.5)
    (re.compile(r"([A-Za-z]+)(\d+)"), r"\1\2"),
    # Inches markings (e.g. 1/2" -> 1/2-inch, 2" -> 2-inch)
    (re.compile(r'(\d+)"'), r"\1-inch"),
    # Degree or temperature / angle symbols
    (re.compile(r"(\d+)\s*°"), r"\1-deg"),
    # Grade markings like 8.8 -> 8-8 or 10.9 -> 10-9
    (re.compile(r"(\d+)\.(\d+)"), r"\1-\2"),
]


def industrial_slugify(text: str, max_length: int = 255) -> str:
    """
    Custom industrial slugifier tailored for fasteners, machinery parts, nuts & bolts.
    
    Preserves:
    - Fractions (e.g., 1/2" -> half-inch)
    - Thread dimensions (e.g., M12 x 1.75 -> m12-x-1-75)
    - Decimal grades (e.g., 8.8, 10.9, 12.9 -> 8-8, 10-9, 12-9)
    - Engineering symbols (dia, UNC, UNF, DIN, ISO, ASTM standards)
    """
    if not text:
        return ""

    normalized = unicodedata.normalize("NFKD", str(text))

    # Replace common fastener fractions
    for frac, replacement in FRACTION_MAP.items():
        normalized = normalized.replace(frac, replacement)

    # Process regex replacements
    for pattern, repl in SYMBOL_REPLACEMENTS:
        normalized = pattern.sub(repl, normalized)

    # Replace forward and backward slashes with dashes
    normalized = normalized.replace("/", "-").replace("\\", "-")

    # Use standard slugify for lowercase, ascii, hyphens
    slug = slugify(normalized)

    # Strip excess consecutive hyphens
    slug = re.sub(r"-{2,}", "-", slug).strip("-")

    if max_length and len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")

    return slug
