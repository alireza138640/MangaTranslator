from pathlib import Path
from typing import List, Tuple

from PIL import ImageFont
import arabic_reshaper
from bidi.algorithm import get_display


FONT_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "fonts"
    / "Vazirmatn-Regular.ttf"
)


def is_rtl_text(text: str) -> bool:
    if not text:
        return False

    rtl_count = 0
    ltr_count = 0

    for char in text:
        code = ord(char)

        if (
            0x0600 <= code <= 0x06FF
            or 0x0750 <= code <= 0x077F
            or 0x08A0 <= code <= 0x08FF
            or 0xFB50 <= code <= 0xFDFF
            or 0xFE70 <= code <= 0xFEFF
        ):
            rtl_count += 1

        elif char.isalpha():
            ltr_count += 1

    return rtl_count > ltr_count


def prepare_text_for_render(text: str) -> str:
    """
    آماده‌سازی متن فارسی برای Pillow.
    """

    text = str(text).strip()

    if not text:
        return ""

    if is_rtl_text(text):
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text

    return text


def load_font(size: int, bold: bool = False):

    if bold:
        path = FONT_PATH.parent / "Vazirmatn-Bold.ttf"
    else:
        path = FONT_PATH

    if not path.exists():
        raise FileNotFoundError(
            f"Font not found: {path}"
        )

    return ImageFont.truetype(
        str(path),
        int(size),
    )


def measure_text(text: str, font) -> Tuple[int, int]:

    prepared = prepare_text_for_render(text)

    if not prepared:
        return 0, 0

    bbox = font.getbbox(prepared)

    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]

    return width, height


def _measure_line(text: str, font) -> Tuple[int, int]:
    return measure_text(text, font)


def wrap_text(
    text: str,
    font,
    max_width: int,
) -> List[str]:

    text = str(text).strip()

    if not text:
        return []

    if max_width <= 0:
        return [text]

    # شکست دستی
    paragraphs = text.replace("\r\n", "\n").split("\n")

    result = []

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            result.append("")
            continue

        words = paragraph.split()

        if not words:
            continue

        current = words[0]

        for word in words[1:]:

            candidate = current + " " + word

            width, _ = _measure_line(
                candidate,
                font,
            )

            if width <= max_width:
                current = candidate
            else:
                result.append(current)
                current = word

        if current:
            result.append(current)

    return result


def fit_multiline_text(
    text: str,
    box_width: int,
    box_height: int,
    min_size: int = 8,
    max_size: int = 64,
    bold: bool = False,
    line_spacing: float = 0.18,
):

    box_width = max(1, int(box_width))
    box_height = max(1, int(box_height))

    best = None

    for size in range(
        int(max_size),
        int(min_size) - 1,
        -1,
    ):

        font = load_font(
            size,
            bold=bold,
        )

        lines = wrap_text(
            text,
            font,
            box_width,
        )

        if not lines:
            continue

        line_heights = []

        valid = True

        for line in lines:

            width, height = _measure_line(
                line,
                font,
            )

            if width > box_width:
                valid = False
                break

            line_heights.append(height)

        if not valid:
            continue

        base_height = max(
            line_heights
        )

        spacing = max(
            1,
            int(size * line_spacing),
        )

        total_height = (
            sum(line_heights)
            + spacing * (len(lines) - 1)
        )

        if total_height <= box_height:

            best = (
                font,
                lines,
                base_height,
                total_height,
                spacing,
            )

            break

    # اگر حتی کوچک‌ترین فونت هم جا نشد
    if best is None:

        font = load_font(
            min_size,
            bold=bold,
        )

        lines = wrap_text(
            text,
            font,
            box_width,
        )

        line_heights = [
            _measure_line(line, font)[1]
            for line in lines
        ]

        base_height = max(
            line_heights,
            default=min_size,
        )

        spacing = max(
            1,
            int(min_size * line_spacing),
        )

        total_height = (
            sum(line_heights)
            + spacing * max(
                0,
                len(lines) - 1,
            )
        )

        best = (
            font,
            lines,
            base_height,
            total_height,
            spacing,
        )

    return best


def fit_font(
    text: str,
    box_width: int,
    box_height: int,
    min_size: int = 8,
    max_size: int = 64,
    bold: bool = False,
):

    font, _, _, _, _ = fit_multiline_text(
        text=text,
        box_width=box_width,
        box_height=box_height,
        min_size=min_size,
        max_size=max_size,
        bold=bold,
    )

    return font


def center_text_position(
    box,
    text,
    font,
):
    left, top, right, bottom = box

    width, height = measure_text(
        text,
        font,
    )

    x = left + (
        right - left - width
    ) / 2

    y = top + (
        bottom - top - height
    ) / 2

    return int(x), int(y)