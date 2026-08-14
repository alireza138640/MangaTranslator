from typing import List, Dict, Any


# =========================================================
# Box utilities
# =========================================================

def get_box_info(box):
    if not box or len(box) != 4:
        return None

    # حالت استاندارد:
    # [left, top, right, bottom]

    xs = []
    ys = []

    for point in box:
        if isinstance(point, (list, tuple)):
            if len(point) < 2:
                return None

            xs.append(float(point[0]))
            ys.append(float(point[1]))
        else:
            return None

    left = min(xs)
    right = max(xs)
    top = min(ys)
    bottom = max(ys)

    if right <= left or bottom <= top:
        return None

    return {
        "left": left,
        "right": right,
        "top": top,
        "bottom": bottom,
        "center_x": (left + right) / 2,
        "center_y": (top + bottom) / 2,
        "width": right - left,
        "height": bottom - top,
    }


def get_item_geometry(item):
    """
    Supports both:

    1. {
        "box": [left, top, right, bottom]
    }

    2. {
        "x": ...,
        "y": ...,
        "width": ...,
        "height": ...
    }
    """

    # -----------------------------------------------------
    # حالت اول: box
    # -----------------------------------------------------

    box = item.get("box")

    if box:
        info = get_box_info(box)

        if info is not None:
            return info

    # -----------------------------------------------------
    # حالت دوم: x/y/width/height
    # -----------------------------------------------------

    if all(
        key in item
        for key in (
            "x",
            "y",
            "width",
            "height",
        )
    ):
        left = float(item["x"])
        top = float(item["y"])
        width = float(item["width"])
        height = float(item["height"])

        right = left + width
        bottom = top + height

        if right <= left or bottom <= top:
            return None

        return {
            "left": left,
            "right": right,
            "top": top,
            "bottom": bottom,
            "center_x": (left + right) / 2,
            "center_y": (top + bottom) / 2,
            "width": width,
            "height": height,
        }

    return None


def horizontal_gap(a, b):
    if a["right"] < b["left"]:
        return b["left"] - a["right"]

    if b["right"] < a["left"]:
        return a["left"] - b["right"]

    return 0


def vertical_gap(a, b):
    if a["bottom"] < b["top"]:
        return b["top"] - a["bottom"]

    if b["bottom"] < a["top"]:
        return a["top"] - b["bottom"]

    return 0


def horizontal_overlap(a, b):
    left = max(
        a["left"],
        b["left"],
    )

    right = min(
        a["right"],
        b["right"],
    )

    if right <= left:
        return 0

    return right - left


def horizontal_overlap_ratio(a, b):
    overlap = horizontal_overlap(
        a,
        b,
    )

    if overlap <= 0:
        return 0.0

    smaller_width = min(
        a["width"],
        b["width"],
    )

    if smaller_width <= 0:
        return 0.0

    return overlap / smaller_width


# =========================================================
# Same line
# =========================================================

def same_line(a, b):

    avg_height = (
        a["height"] +
        b["height"]
    ) / 2

    if avg_height <= 0:
        return False

    center_distance = abs(
        a["center_y"] -
        b["center_y"]
    )

    # خطوط باید از نظر عمودی نزدیک باشند
    if center_distance > avg_height * 0.65:
        return False

    gap = horizontal_gap(
        a,
        b,
    )

    # فاصله خیلی زیاد
    if gap > avg_height * 4.0:
        return False

    return True


# =========================================================
# Same text block
# =========================================================

def same_block(a, b):

    avg_height = (
        a["height"] +
        b["height"]
    ) / 2

    if avg_height <= 0:
        return False

    vgap = vertical_gap(
        a,
        b,
    )

    # فاصله عمودی بیش از حد
    if vgap > avg_height * 1.8:
        return False

    overlap = horizontal_overlap_ratio(
        a,
        b,
    )

    # -----------------------------------------------------
    # حالت 1:
    # overlap قابل توجه
    # -----------------------------------------------------

    if overlap >= 0.55:
        return True

    # -----------------------------------------------------
    # حالت 2:
    # overlap متوسط + عرض مشابه
    # -----------------------------------------------------

    width_a = max(
        1,
        a["width"],
    )

    width_b = max(
        1,
        b["width"],
    )

    width_ratio = (
        min(width_a, width_b)
        /
        max(width_a, width_b)
    )

    if (
        overlap >= 0.35
        and
        width_ratio >= 0.65
    ):
        return True

    # -----------------------------------------------------
    # حالت 3:
    # خطوط باریک پشت سر هم
    # -----------------------------------------------------

    center_distance_x = abs(
        a["center_x"] -
        b["center_x"]
    )

    max_center_distance = (
        max(
            a["width"],
            b["width"],
        )
        * 0.35
    )

    if (
        overlap >= 0.20
        and
        center_distance_x <= max_center_distance
    ):
        return True

    return False


# =========================================================
# Group lines
# =========================================================

def group_lines(
    ocr_results,
):

    items = []

    # -----------------------------------------------------
    # تبدیل OCR به اطلاعات هندسی
    # -----------------------------------------------------

    for item in ocr_results:

        # ---------------------------------------------
        # پشتیبانی از OCRResult object
        # ---------------------------------------------

        if hasattr(item, "to_dict"):
            item = item.to_dict()

        if not isinstance(item, dict):
            continue

        text = str(
            item.get(
                "text",
                "",
            )
        ).strip()

        if not text:
            continue

        geometry = get_item_geometry(
            item
        )

        if geometry is None:
            print(
                "[Grouping] "
                f"Skipped item without geometry: "
                f"{text!r}"
            )
            continue

        items.append(
            {
                **item,
                **geometry,
            }
        )

    if not items:
        print(
            "[Grouping] "
            "No valid OCR items."
        )

        return []

    # -----------------------------------------------------
    # مرتب‌سازی
    # -----------------------------------------------------

    items.sort(
        key=lambda x: (
            x["center_y"],
            x["left"],
        )
    )

    # -----------------------------------------------------
    # ساخت خطوط
    # -----------------------------------------------------

    lines = []

    for item in items:

        best_line = None
        best_distance = float("inf")

        for line in lines:

            line_top = min(
                x["top"]
                for x in line
            )

            line_bottom = max(
                x["bottom"]
                for x in line
            )

            line_center_y = (
                line_top +
                line_bottom
            ) / 2

            line_height = max(
                x["height"]
                for x in line
            )

            distance = abs(
                item["center_y"] -
                line_center_y
            )

            if distance > (
                line_height * 0.65
            ):
                continue

            connected = False

            for existing in line:

                if same_line(
                    item,
                    existing,
                ):
                    connected = True
                    break

            if not connected:
                continue

            if distance < best_distance:

                best_distance = distance
                best_line = line

        if best_line is not None:

            best_line.append(
                item
            )

        else:

            lines.append(
                [item]
            )

    # -----------------------------------------------------
    # مرتب‌سازی داخل خطوط
    # -----------------------------------------------------

    for line in lines:

        line.sort(
            key=lambda x:
                x["left"]
        )

    # -----------------------------------------------------
    # ساخت line objects
    # -----------------------------------------------------

    line_objects = []

    for line in lines:

        left = min(
            x["left"]
            for x in line
        )

        right = max(
            x["right"]
            for x in line
        )

        top = min(
            x["top"]
            for x in line
        )

        bottom = max(
            x["bottom"]
            for x in line
        )

        line_objects.append(
            {
                "items": line,

                "left": left,
                "right": right,

                "top": top,
                "bottom": bottom,

                "center_x":
                    (left + right) / 2,

                "center_y":
                    (top + bottom) / 2,

                "width":
                    right - left,

                "height":
                    bottom - top,
            }
        )

    # -----------------------------------------------------
    # مرتب‌سازی خطوط
    # -----------------------------------------------------

    line_objects.sort(
        key=lambda line: (
            line["top"],
            line["left"],
        )
    )

    # -----------------------------------------------------
    # ساخت blocks
    # -----------------------------------------------------

    blocks = []

    for line in line_objects:

        best_block = None
        best_distance = float(
            "inf"
        )

        for block in blocks:

            for existing in block:

                if not same_block(
                    line,
                    existing,
                ):
                    continue

                hgap = horizontal_gap(
                    line,
                    existing,
                )

                vgap = vertical_gap(
                    line,
                    existing,
                )

                distance = (
                    hgap +
                    vgap
                )

                if distance < best_distance:

                    best_distance = distance
                    best_block = block

        if best_block is not None:

            best_block.append(
                line
            )

        else:

            blocks.append(
                [line]
            )

    # -----------------------------------------------------
    # مرتب‌سازی داخل block
    # -----------------------------------------------------

    for block in blocks:

        block.sort(
            key=lambda line: (
                line["top"],
                line["left"],
            )
        )

    # -----------------------------------------------------
    # تبدیل به OCR groups
    # -----------------------------------------------------

    result = []

    for block in blocks:

        all_items = []

        for line in block:

            all_items.extend(
                line["items"]
            )

        if all_items:

            result.append(
                all_items
            )

    # -----------------------------------------------------
    # مرتب‌سازی نهایی
    # -----------------------------------------------------

    result.sort(
        key=lambda block: (
            min(
                x["top"]
                for x in block
            ),
            min(
                x["left"]
                for x in block
            ),
        )
    )

    # -----------------------------------------------------
    # DEBUG
    # -----------------------------------------------------

    print(
        f"[Grouping] "
        f"Lines={len(lines)} "
        f"Blocks={len(result)}"
    )

    for index, block in enumerate(
        result,
        start=1,
    ):

        texts = [
            x["text"]
            for x in block
        ]

        left = min(
            x["left"]
            for x in block
        )

        top = min(
            x["top"]
            for x in block
        )

        right = max(
            x["right"]
            for x in block
        )

        bottom = max(
            x["bottom"]
            for x in block
        )

        print(
            f"[Grouping] "
            f"{index:02} "
            f"box=({int(left)},"
            f"{int(top)},"
            f"{int(right)},"
            f"{int(bottom)}) "
            f"text={texts}"
        )

    return result


# =========================================================
# Merge groups
# =========================================================

def merge_groups(
    groups,
):

    output = []

    for group in groups:

        if not group:
            continue

        group = sorted(
            group,
            key=lambda x: (
                x["top"],
                x["left"],
            ),
        )

        text = " ".join(
            x["text"]
            for x in group
            if x.get(
                "text",
                "",
            ).strip()
        )

        if not text:
            continue

        left = min(
            x["left"]
            for x in group
        )

        top = min(
            x["top"]
            for x in group
        )

        right = max(
            x["right"]
            for x in group
        )

        bottom = max(
            x["bottom"]
            for x in group
        )

        confidence = (
            sum(
                float(
                    x.get(
                        "confidence",
                        0.0,
                    )
                )
                for x in group
            )
            /
            len(group)
        )

        output.append(
            {
                "text":
                    text.strip(),

                "box": [
                    int(left),
                    int(top),
                    int(right),
                    int(bottom),
                ],

                "confidence":
                    confidence,

                "items":
                    group,
            }
        )

    return output