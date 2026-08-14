import numpy as np

from typing import List, Dict, Any

from PIL import Image, ImageDraw

from .text import (
    fit_multiline_text,
    prepare_text_for_render,
)


# =========================================================
# TEXT COLOR
# =========================================================

def choose_text_color(
    image: Image.Image,
    box,
):
    """
    انتخاب رنگ متن بر اساس روشن یا تاریک بودن ناحیه پشت متن.

    برای حباب سفید:
        متن مشکی

    برای حباب/پس‌زمینه مشکی:
        متن سفید
    """

    normalized = normalize_box(box)

    if normalized is None:
        return (
            20,
            20,
            20,
        )

    left, top, right, bottom = normalized

    crop = image.crop(
        (
            left,
            top,
            right,
            bottom,
        )
    )

    gray = crop.convert("L")

    array = np.asarray(
        gray,
        dtype=np.float32,
    )

    if array.size == 0:
        return (
            20,
            20,
            20,
        )

    # -----------------------------------------------------
    # تعداد پیکسل‌های تاریک
    # -----------------------------------------------------

    dark_ratio = float(
        np.mean(
            array < 128
        )
    )

    # -----------------------------------------------------
    # میانگین و میانه
    # -----------------------------------------------------

    brightness_mean = float(
        np.mean(array)
    )

    brightness_median = float(
        np.median(array)
    )

    # -----------------------------------------------------
    # پس‌زمینه کاملاً تاریک
    # -----------------------------------------------------

    if dark_ratio >= 0.58:
        return (
            245,
            245,
            245,
        )

    # -----------------------------------------------------
    # پس‌زمینه کاملاً روشن
    # -----------------------------------------------------

    if dark_ratio <= 0.42:
        return (
            20,
            20,
            20,
        )

    # -----------------------------------------------------
    # حالت ترکیبی
    # -----------------------------------------------------

    brightness = (
        brightness_mean * 0.45
        + brightness_median * 0.55
    )

    if brightness < 115:
        return (
            245,
            245,
            245,
        )

    return (
        20,
        20,
        20,
    )


# =========================================================
# BOX
# =========================================================

def normalize_box(box):

    if not box:
        return None

    if len(box) != 4:
        return None

    try:

        left, top, right, bottom = map(
            int,
            box,
        )

    except (
        TypeError,
        ValueError,
    ):
        return None

    if right <= left:
        return None

    if bottom <= top:
        return None

    return (
        left,
        top,
        right,
        bottom,
    )


# =========================================================
# DRAW MULTILINE
# =========================================================

def _draw_multiline_centered(
    draw,
    lines,
    font,
    box,
    line_spacing,
    text_color,
):
    """
    رسم متن چندخطی در مرکز box.
    """

    left, top, right, bottom = box

    box_width = right - left
    box_height = bottom - top

    measurements = []

    total_height = 0

    # -----------------------------------------------------
    # اندازه‌گیری خطوط
    # -----------------------------------------------------

    for line in lines:

        prepared = prepare_text_for_render(
            line
        )

        if not prepared:
            continue

        bbox = font.getbbox(
            prepared
        )

        text_width = (
            bbox[2] - bbox[0]
        )

        text_height = (
            bbox[3] - bbox[1]
        )

        measurements.append(
            (
                prepared,
                text_width,
                text_height,
                bbox,
            )
        )

        total_height += text_height

    if not measurements:
        return

    # -----------------------------------------------------
    # فاصله بین خطوط
    # -----------------------------------------------------

    if len(measurements) > 1:

        total_height += (
            line_spacing
            * (len(measurements) - 1)
        )

    # -----------------------------------------------------
    # شروع عمودی
    # -----------------------------------------------------

    y = top + (
        box_height - total_height
    ) / 2

    # -----------------------------------------------------
    # رسم
    # -----------------------------------------------------

    for (
        prepared,
        text_width,
        text_height,
        bbox,
    ) in measurements:

        x = left + (
            box_width - text_width
        ) / 2

        # getbbox ممکن است offset منفی داشته باشد
        draw_y = y - bbox[1]

        draw.text(
            (
                int(x),
                int(draw_y),
            ),
            prepared,
            font=font,
            fill=text_color,
        )

        y += (
            text_height
            + line_spacing
        )


# =========================================================
# RENDER SINGLE BLOCK
# =========================================================

def render_text_block(
    image: Image.Image,
    block: Dict[str, Any],
):

    if image is None:
        raise ValueError(
            "image cannot be None"
        )

    # -----------------------------------------------------
    # متن ترجمه
    # -----------------------------------------------------

    text = str(
        block.get(
            "translated_text",
            "",
        )
    ).strip()

    if not text:
        return image

    # -----------------------------------------------------
    # box
    # -----------------------------------------------------

    box = normalize_box(
        block.get("box")
    )

    if box is None:
        print(
            "[Renderer] Invalid box:",
            block.get("box"),
        )

        return image

    left, top, right, bottom = box

    width = right - left
    height = bottom - top

    if width <= 1 or height <= 1:
        return image

    # -----------------------------------------------------
    # padding
    #
    # خیلی بزرگش نمی‌کنیم چون باعث کوچک شدن فضای متن
    # و بعد انتخاب رفتار عجیب fit_multiline می‌شود.
    # -----------------------------------------------------

    padding = max(
        3,
        min(
            12,
            int(
                min(width, height)
                * 0.045
            ),
        ),
    )

    inner_left = left + padding
    inner_top = top + padding
    inner_right = right - padding
    inner_bottom = bottom - padding

    inner_width = max(
        1,
        inner_right - inner_left,
    )

    inner_height = max(
        1,
        inner_bottom - inner_top,
    )

    inner_box = (
        inner_left,
        inner_top,
        inner_right,
        inner_bottom,
    )

    # -----------------------------------------------------
    # انتخاب رنگ متن
    # -----------------------------------------------------

    text_color = choose_text_color(
        image,
        inner_box,
    )

    # -----------------------------------------------------
    # اندازه فونت
    #
    # سقف را کمی منطقی‌تر نگه می‌داریم تا ترجمه‌ها
    # بی‌دلیل غول‌پیکر نشوند.
    # -----------------------------------------------------

    max_font_size = min(
        48,
        max(
            12,
            int(
                inner_height
                * 0.70
            ),
        ),
    )

    # -----------------------------------------------------
    # Fit text
    # -----------------------------------------------------

    (
        font,
        lines,
        line_height,
        total_height,
        line_spacing,
    ) = fit_multiline_text(
        text=text,
        box_width=inner_width,
        box_height=inner_height,
        min_size=8,
        max_size=max_font_size,
        bold=False,
        line_spacing=0.18,
    )

    # -----------------------------------------------------
    # Debug
    # -----------------------------------------------------

    print(
        "[Render]"
        f" text='{text}'"
        f" box={box}"
        f" area={inner_width}x{inner_height}"
        f" font={font.size}"
        f" lines={len(lines)}"
        f" text_lines={lines}"
        f" color={text_color}"
    )

    # -----------------------------------------------------
    # رسم
    # -----------------------------------------------------

    draw = ImageDraw.Draw(
        image
    )

    _draw_multiline_centered(
        draw=draw,
        lines=lines,
        font=font,
        box=inner_box,
        line_spacing=line_spacing,
        text_color=text_color,
    )

    return image


# =========================================================
# RENDER ALL BLOCKS
# =========================================================

def render_text_blocks(
    image: Image.Image,
    blocks: List[Dict[str, Any]],
):

    if image is None:
        raise ValueError(
            "image cannot be None"
        )

    if not blocks:
        return image

    for index, block in enumerate(
        blocks,
        start=1,
    ):

        try:

            render_text_block(
                image,
                block,
            )

        except Exception as exc:

            print(
                "[Renderer]"
                f" Failed to render block #{index}:"
                f" {exc}"
            )

    return image


# =========================================================
# RENDER IMAGE
# =========================================================

def render_image(
    image: Image.Image,
    blocks: List[Dict[str, Any]],
):

    if image is None:
        raise ValueError(
            "image cannot be None"
        )

    result = image.copy()

    render_text_blocks(
        result,
        blocks,
    )

    return result