from ocr.detector import OCRDetector
from ocr.grouping import group_lines, merge_groups
from ocr.cleaner import clean_groups
from ocr.correction import correct_groups
from ocr.result import build_ocr_blocks
from ocr.validator import validate_blocks


class OCRManager:

    def __init__(self, lang="en"):

        self.lang = lang

        # ---------------------------------
        # OCR Detector
        # ---------------------------------

        self.detector = OCRDetector()

    # =========================================================
    # OCR
    # =========================================================

    def recognize(self, image_path):

        # ---------------------------------
        # 1. OCR Detection
        # ---------------------------------

        results = self.detector.detect(
            image_path
        )

        # ---------------------------------
        # اگر OCR هیچ نتیجه‌ای نداد
        # ---------------------------------

        if not results:

            print(
                "[OCRManager] No OCR results."
            )

            return []

        # ---------------------------------
        # 2. Grouping
        # ---------------------------------

        groups = group_lines(
            results
        )

        # ---------------------------------
        # 3. Merge Groups
        # ---------------------------------

        merged = merge_groups(
            groups
        )

        # ---------------------------------
        # 4. Cleaning
        # ---------------------------------

        cleaned = clean_groups(
            merged
        )

        # ---------------------------------
        # 5. Correction
        # ---------------------------------

        corrected = correct_groups(
            cleaned
        )

        # ---------------------------------
        # 6. Build OCR Blocks
        # ---------------------------------

        blocks = build_ocr_blocks(
            corrected
        )

        # ---------------------------------
        # اگر block ساخته نشد
        # ---------------------------------

        if not blocks:

            print(
                "[OCRManager] No OCR blocks."
            )

            return []

        # ---------------------------------
        # 7. Validation
        # ---------------------------------

        blocks = validate_blocks(
            blocks
        )

        # ---------------------------------
        # گزارش نهایی
        # ---------------------------------

        accepted = sum(
            1
            for block in blocks
            if getattr(
                block,
                "status",
                None
            ) == "accepted"
        )

        review = sum(
            1
            for block in blocks
            if getattr(
                block,
                "status",
                None
            ) == "review"
        )

        print(
            "[OCRManager] "
            f"Blocks={len(blocks)} "
            f"Accepted={accepted} "
            f"Review={review}"
        )

        return blocks