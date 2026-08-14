from dataclasses import dataclass, field
from typing import Any


@dataclass
class OCRBlock:

    id: int
    text: str
    box: list[int]
    confidence: float
    items: list[dict[str, Any]] = field(
        default_factory=list
    )
    status: str = "accepted"
    validation: dict = field(
    default_factory=dict
)

    @property
    def left(self):
        return self.box[0]

    @property
    def top(self):
        return self.box[1]

    @property
    def right(self):
        return self.box[2]

    @property
    def bottom(self):
        return self.box[3]

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def center(self):
        return (
            (self.left + self.right) / 2,
            (self.top + self.bottom) / 2,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "box": self.box,
            "confidence": self.confidence,
            "items": self.items,
            "status": self.status,
            "validation": self.validation,
        }


def build_ocr_blocks(groups):

    blocks = []

    for index, group in enumerate(groups, start=1):

        text = str(
            group.get("text", "")
        ).strip()

        if not text:
            continue

        confidence = float(
            group.get("confidence", 0.0)
        )

        # ---------------------------------
        # تعیین وضعیت
        # ---------------------------------

        if confidence < 0.85:
            status = "review"

        else:
            status = "accepted"

        block = OCRBlock(
            id=index,
            text=text,
            box=[
                int(group["box"][0]),
                int(group["box"][1]),
                int(group["box"][2]),
                int(group["box"][3]),
            ],
            confidence=confidence,
            items=group.get(
                "items",
                []
            ),
            status=status,
        )

        blocks.append(block)

    return blocks


def print_ocr_blocks(blocks):

    print(
        f"OCR Blocks: {len(blocks)}"
    )

    print("-" * 70)

    for block in blocks:

        print(
            f"{block.id:02d} | "
            f"{block.status:<8} | "
            f"conf={block.confidence:.3f} | "
            f"box={block.box}"
        )

        print(
            f"    {block.text}"
        )

    print("-" * 70)