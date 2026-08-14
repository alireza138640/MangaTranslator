from paddleocr import PaddleOCR

from ocr.models import OCRResult


class OCRDetector:

    def __init__(self):

        self.ocr = PaddleOCR(
            lang="en",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

        # حداقل اطمینان OCR
        self.min_confidence = 0.60


    def detect(
        self,
        image_path,
    ):

        result = self.ocr.predict(
            image_path
        )

        results = []

        for page in result:

            data = page.json

            # PaddleOCR جدید داده‌ها را داخل res نگه می‌دارد
            if "res" in data:
                data = data["res"]

            texts = data.get(
                "rec_texts",
                [],
            )

            scores = data.get(
                "rec_scores",
                [],
            )

            boxes = data.get(
                "rec_boxes",
                [],
            )

            if not texts:
                continue

            for text, score, box in zip(
                texts,
                scores,
                boxes,
            ):

                text = str(
                    text
                ).strip()

                score = float(
                    score
                )

                # ---------------------------------
                # حذف OCRهای بسیار ضعیف
                # ---------------------------------

                if score < self.min_confidence:
                    print(
                        "[OCR] Skipped low confidence:"
                        f" '{text}'"
                        f" score={score:.3f}"
                    )

                    continue

                if not text:
                    continue

                # ---------------------------------
                # اعتبارسنجی box
                # ---------------------------------

                if box is None:
                    continue

                if len(box) != 4:
                    continue

                x1 = int(
                    box[0]
                )

                y1 = int(
                    box[1]
                )

                x2 = int(
                    box[2]
                )

                y2 = int(
                    box[3]
                )

                if x2 <= x1:
                    continue

                if y2 <= y1:
                    continue

                width = x2 - x1
                height = y2 - y1

                # ---------------------------------
                # حذف نواحی غیرطبیعی
                #
                # OCRهای خیلی باریک/خیلی بلند
                # معمولاً نویز یا اشتباه هستند.
                # ---------------------------------

                if width <= 2 or height <= 2:
                    continue

                # ---------------------------------
                # جلوگیری از boxهای بسیار بلند
                #
                # متن معمولی نباید مثل یک خط
                # عمودی 200 پیکسلی باشد.
                # ---------------------------------

                if (
                    height > 120
                    and height > width * 2.5
                ):
                    print(
                        "[OCR] Skipped abnormal box:"
                        f" '{text}'"
                        f" box=({x1},{y1},{x2},{y2})"
                    )

                    continue

                results.append(
                    OCRResult(
                        text,
                        x1,
                        y1,
                        width,
                        height,
                        score,
                    )
                )

        print(
            f"[OCR] Accepted blocks: {len(results)}"
        )

        return results