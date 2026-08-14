from typing import Dict, Any, List, Tuple


def box_to_rect(box) -> Tuple[int, int, int, int]:

    if not box or len(box) != 4:
        raise ValueError("Invalid box")

    left, top, right, bottom = box

    return (
        int(left),
        int(top),
        int(right),
        int(bottom),
    )


def get_box_size(box) -> Tuple[int, int]:

    left, top, right, bottom = box_to_rect(box)

    width = max(1, right - left)
    height = max(1, bottom - top)

    return width, height


def get_box_center(box) -> Tuple[int, int]:

    left, top, right, bottom = box_to_rect(box)

    center_x = (left + right) // 2
    center_y = (top + bottom) // 2

    return center_x, center_y


def calculate_font_size(
    box,
    base_size: int = 24,
    min_size: int = 10,
    max_size: int = 48,
) -> int:

    _, height = get_box_size(
        box
    )

    # Conservative font size.
    #
    # The old value used 65% of the box height,
    # which could produce oversized Persian text
    # when OCR merged a large region.
    size = int(
        height * 0.45
    )

    size = max(
        min_size,
        size,
    )

    size = min(
        max_size,
        size,
    )

    return size


def calculate_text_area(
    box,
    padding: int = 4,
) -> Dict[str, int]:

    left, top, right, bottom = box_to_rect(box)

    return {
        "left": left + padding,
        "top": top + padding,
        "right": max(left + padding + 1, right - padding),
        "bottom": max(top + padding + 1, bottom - padding),
    }


def fit_text_size(
    draw,
    text: str,
    font_loader,
    area_width: int,
    area_height: int,
    start_size: int,
    min_size: int = 8,
):

    if not text:
        return None

    size = start_size

    while size >= min_size:

        font = font_loader(size)

        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font,
        )

        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        if (
            width <= area_width
            and height <= area_height
        ):
            return font

        size -= 1

    return font_loader(min_size)


def calculate_text_position(
    box,
    text_size: Tuple[int, int],
):

    left, top, right, bottom = box_to_rect(box)

    text_width, text_height = text_size

    box_width = right - left
    box_height = bottom - top

    x = left + max(
        0,
        (box_width - text_width) // 2,
    )

    y = top + max(
        0,
        (box_height - text_height) // 2,
    )

    return x, y


def prepare_layout(
    block: Dict[str, Any],
    padding: int = 4,
) -> Dict[str, Any]:

    box = block.get("box")

    if not box:
        return {
            "valid": False,
            "reason": "missing_box",
        }

    rect = box_to_rect(box)

    width, height = get_box_size(rect)

    area = calculate_text_area(
        rect,
        padding=padding,
    )

    font_size = calculate_font_size(
        rect
    )

    return {
        "valid": True,
        "box": rect,
        "width": width,
        "height": height,
        "text_area": area,
        "font_size": font_size,
    }


def prepare_layouts(
    blocks: List[Dict[str, Any]],
    padding: int = 4,
) -> List[Dict[str, Any]]:

    layouts = []

    for block in blocks:

        layout = prepare_layout(
            block,
            padding=padding,
        )

        layouts.append({
            "block": block,
            "layout": layout,
        })

    return layouts