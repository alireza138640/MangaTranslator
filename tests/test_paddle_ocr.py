import paddle

paddle.set_flags({
    "FLAGS_use_onednn": False
})

from paddleocr import PaddleOCR


def main():
    print("=" * 60)
    print("PaddleOCR standalone test")
    print("=" * 60)

    print("Paddle:", paddle.__version__)

    ocr = PaddleOCR(
        lang="en",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )

    image_path = "samples/page_001.jpeg"

    print(f"Image: {image_path}")
    print("Running OCR...")

    results = ocr.predict(image_path)

    count = 0

    for result in results:

        texts = result.get("rec_texts", [])
        scores = result.get("rec_scores", [])
        boxes = result.get("rec_polys", [])

        for i, text in enumerate(texts):

            if not text:
                continue

            confidence = 0.0

            if i < len(scores):
                confidence = float(scores[i])

            box = []

            if i < len(boxes):
                box = boxes[i].tolist()

            if not box:
                continue

            count += 1

            print()
            print(f"[{count}]")
            print("TEXT:", repr(str(text).strip()))
            print("CONF:", round(confidence, 3))
            print("BOX:", box)

    print()
    print("=" * 60)
    print("OCR COUNT:", count)
    print("=" * 60)


if __name__ == "__main__":
    main()