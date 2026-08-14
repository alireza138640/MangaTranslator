from typing import List, Dict, Any

import cv2
import numpy as np
from PIL import Image


# =========================================================
# Text cleaning
# =========================================================

def clean_groups(
    groups: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    cleaned = []

    for group in groups:

        if not group:
            continue

        item = dict(group)

        text = str(
            item.get("text", "")
        ).strip()

        if not text:
            continue

        # فاصله‌های اضافی
        text = " ".join(
            text.split()
        )

        item["text"] = text

        cleaned.append(item)

    return cleaned


# =========================================================
# Create text mask
# =========================================================

def create_text_mask(
    image_size,
    blocks: List[Dict[str, Any]],
    padding: int = 2,
):

    width, height = image_size

    mask = np.zeros(
        (height, width),
        dtype=np.uint8,
    )

    for block in blocks:

        polygon = block.get("polygon")

        if polygon and len(polygon) >= 4:

            points = np.array(
                polygon,
                dtype=np.int32
            )

            cv2.fillPoly(
                mask,
                [points],
                255
            )

            continue

        box = block.get("box")

        if not box or len(box) != 4:
            continue

        left, top, right, bottom = map(
            int,
            box
        )

        left = max(
            0,
            left - padding
        )

        top = max(
            0,
            top - padding
        )

        right = min(
            width - 1,
            right + padding
        )

        bottom = min(
            height - 1,
            bottom + padding
        )

        if right <= left or bottom <= top:
            continue

        cv2.rectangle(
            mask,
            (left, top),
            (right, bottom),
            255,
            thickness=-1
        )

    return Image.fromarray(
        mask,
        mode="L"
    )


# =========================================================
# Remove text regions
# =========================================================

def remove_text_regions(
    image: Image.Image,
    blocks: List[Dict[str, Any]],
    padding: int = 2,
    radius: float = 2.0,
):

    if image is None:
        raise ValueError(
            "image cannot be None"
        )

    image = image.convert("RGB")

    mask_image = create_text_mask(
        image.size,
        blocks,
        padding=padding
    )

    image_np = np.array(
        image,
        dtype=np.uint8
    )

    mask_np = np.array(
        mask_image,
        dtype=np.uint8
    )

    if not np.any(mask_np):
        return image.copy(), mask_image

    result_np = cv2.inpaint(
        image_np,
        mask_np,
        radius,
        cv2.INPAINT_TELEA
    )

    result = Image.fromarray(
        result_np,
        mode="RGB"
    )

    return result, mask_image