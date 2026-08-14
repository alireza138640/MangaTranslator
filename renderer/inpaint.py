from typing import List, Dict, Any

import cv2
import numpy as np

from PIL import Image


def _polygon_from_item(item):

    box = item.get("box")

    if not box:
        return None

    if len(box) < 4:
        return None

    points = []

    for point in box:

        if not isinstance(
            point,
            (list, tuple),
        ):
            continue

        if len(point) < 2:
            continue

        points.append(
            [
                int(point[0]),
                int(point[1]),
            ]
        )

    if len(points) < 4:
        return None

    return np.array(
        points,
        dtype=np.int32,
    )


def _polygon_padding(
    polygon,
    padding,
):

    if padding <= 0:
        return polygon

    center = polygon.mean(
        axis=0,
        keepdims=True,
    )

    direction = polygon - center

    length = np.linalg.norm(
        direction,
        axis=1,
        keepdims=True,
    )

    length[length == 0] = 1

    expanded = (
        polygon
        + direction / length * padding
    )

    return np.round(
        expanded
    ).astype(np.int32)


def create_text_mask(
    image_size,
    blocks: List[Dict[str, Any]],
    padding: int = 1,
):

    width, height = image_size

    mask = np.zeros(
        (height, width),
        dtype=np.uint8,
    )

    for block in blocks:

        items = block.get(
            "items",
            [],
        )

        used_polygon = False

        # ==================================================
        # Use original OCR polygons
        # ==================================================

        for item in items:

            polygon = _polygon_from_item(
                item
            )

            if polygon is None:
                continue

            polygon = _polygon_padding(
                polygon,
                padding,
            )

            polygon[:, 0] = np.clip(
                polygon[:, 0],
                0,
                width - 1,
            )

            polygon[:, 1] = np.clip(
                polygon[:, 1],
                0,
                height - 1,
            )

            cv2.fillPoly(
                mask,
                [polygon],
                255,
            )

            used_polygon = True

        # ==================================================
        # Rectangle fallback
        # ==================================================

        if used_polygon:
            continue

        box = block.get(
            "box"
        )

        if not box or len(box) != 4:
            continue

        left, top, right, bottom = map(
            int,
            box,
        )

        left = max(
            0,
            left - 1,
        )

        top = max(
            0,
            top - 1,
        )

        right = min(
            width - 1,
            right + 1,
        )

        bottom = min(
            height - 1,
            bottom + 1,
        )

        if right <= left or bottom <= top:
            continue

        cv2.rectangle(
            mask,
            (left, top),
            (right, bottom),
            255,
            thickness=-1,
        )

    return Image.fromarray(
        mask,
        mode="L",
    )


def remove_text_regions(
    image: Image.Image,
    blocks: List[Dict[str, Any]],
    padding: int = 1,
    radius: float = 2.0,
):

    if image is None:
        raise ValueError(
            "image cannot be None"
        )

    image = image.convert(
        "RGB"
    )

    mask_image = create_text_mask(
        image.size,
        blocks,
        padding=padding,
    )

    image_np = np.array(
        image,
        dtype=np.uint8,
    )

    mask_np = np.array(
        mask_image,
        dtype=np.uint8,
    )

    # Nothing to remove
    if not np.any(mask_np):
        return (
            image.copy(),
            mask_image,
        )

    # ==================================================
    # Small inpainting radius
    # ==================================================

    result_np = cv2.inpaint(
        image_np,
        mask_np,
        radius,
        cv2.INPAINT_TELEA,
    )

    result = Image.fromarray(
        result_np,
        mode="RGB",
    )

    return (
        result,
        mask_image,
    )