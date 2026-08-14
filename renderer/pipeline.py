from pathlib import Path
from typing import List, Dict, Any

from PIL import Image

from ocr.manager import OCRManager

from translator.manager import TranslationManager

from renderer.inpaint import remove_text_regions
from renderer.layout import prepare_layouts
from renderer.renderer import render_text_blocks


class MangaRendererPipeline:

    def __init__(
        self,
        source_language: str = "en",
        target_language: str = "fa",
        translation_mode: str = "offline",
    ):
        self.source_language = source_language
        self.target_language = target_language

        # =====================================================
        # OCR Manager
        # =====================================================

        self.ocr = OCRManager(
            lang=source_language
        )

        # =====================================================
        # Translation Manager
        # =====================================================

        self.translator = TranslationManager(
            source_language=source_language,
            target_language=target_language,
            mode=translation_mode,
        )

    # =====================================================
    # OCR
    # =====================================================

    def run_ocr(
        self,
        image_path: str,
    ):

        # -----------------------------------------------------
        # OCRManager تمام مراحل OCR را خودش انجام می‌دهد:
        #
        # 1. Detection
        # 2. Grouping
        # 3. Merge
        # 4. Cleaning
        # 5. Correction
        # 6. Build OCR Blocks
        # 7. Validation
        #
        # بنابراین خروجی OCRManager را دوباره وارد
        # group_lines / merge_groups / build_ocr_blocks
        # نمی‌کنیم.
        # -----------------------------------------------------

        blocks = self.ocr.recognize(
            image_path
        )

        return blocks

    # =====================================================
    # Convert OCRBlock to dict
    # =====================================================

    @staticmethod
    def blocks_to_dict(
        blocks,
    ):

        result = []

        for block in blocks:

            result.append(
                {
                    "text": block.text,
                    "box": list(block.box),
                    "confidence": float(block.confidence),
                    "items": list(block.items),
                    "status": block.status,
                    "validation": getattr(
                        block,
                        "validation",
                        {},
                    ),
                }
            )

        return result

    # =====================================================
    # Translation
    # =====================================================

    def translate(
        self,
        blocks,
    ):

        translations = (
            self.translator.translate_blocks(
                blocks
            )
        )

        result = []

        for translation in translations:

            result.append(
                {
                    "text":
                        translation.source_text,

                    "translated_text":
                        translation.translated_text,

                    "box":
                        translation.box,

                    "confidence":
                        translation.confidence,

                    "status":
                        translation.status,

                    "translator":
                        translation.translator,
                }
            )

        return result

    # =====================================================
    # Layout
    # =====================================================

    def prepare_layout(
        self,
        blocks,
    ):

        return prepare_layouts(
            blocks
        )

    # =====================================================
    # Render
    # =====================================================

    def render(
        self,
        image,
        translated_blocks,
    ):

        # -------------------------------------------------
        # حذف متن اصلی
        # -------------------------------------------------

        cleaned_image, mask = (
            remove_text_regions(
                image,
                translated_blocks,
                padding=3,
            )
        )

        # -------------------------------------------------
        # آماده‌سازی Layout
        # -------------------------------------------------

        layouts = self.prepare_layout(
            translated_blocks
        )

        # -------------------------------------------------
        # اتصال Layout به Block
        # -------------------------------------------------

        render_blocks = []

        for block, layout_data in zip(
            translated_blocks,
            layouts,
        ):

            item = dict(
                block
            )

            item["layout"] = (
                layout_data.get(
                    "layout"
                )
            )

            render_blocks.append(
                item
            )

        # -------------------------------------------------
        # Render فارسی
        # -------------------------------------------------

        render_text_blocks(
            cleaned_image,
            render_blocks,
        )

        return (
            cleaned_image,
            mask,
        )

    # =====================================================
    # Process Complete Page
    # =====================================================

    def process_page(
        self,
        input_path: str,
        output_path: str,
    ):

        input_path = Path(
            input_path
        )

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        print()
        print("=" * 70)
        print(
            f"Processing: "
            f"{input_path.name}"
        )
        print("=" * 70)

        # -------------------------------------------------
        # Check Input
        # -------------------------------------------------

        if not input_path.exists():

            raise FileNotFoundError(
                f"Input image not found: "
                f"{input_path}"
            )

        # -------------------------------------------------
        # Load Image
        # -------------------------------------------------

        image = Image.open(
            input_path
        ).convert(
            "RGB"
        )

        print(
            f"Image size: "
            f"{image.size}"
        )

        # =================================================
        # 1/4 OCR
        # =================================================

        print()
        print(
            "[1/4] OCR..."
        )

        ocr_blocks = self.run_ocr(
            str(input_path)
        )

        print(
            f"OCR blocks: "
            f"{len(ocr_blocks)}"
        )

        # -------------------------------------------------
        # نمایش OCR
        # -------------------------------------------------

        for index, block in enumerate(
            ocr_blocks,
            start=1,
        ):

            print(
                f"{index:02} | "
                f"{str(block.status):10} | "
                f"{block.confidence:.3f} | "
                f"{block.text}"
            )

        # =================================================
        # Convert OCR Blocks
        # =================================================

        blocks = self.blocks_to_dict(
            ocr_blocks
        )

        # =================================================
        # 2/4 Translation
        # =================================================

        print()
        print(
            "[2/4] Translation..."
        )

        translated_blocks = self.translate(
            blocks
        )

        print(
            f"Translation blocks: "
            f"{len(translated_blocks)}"
        )

        for index, block in enumerate(
            translated_blocks,
            start=1,
        ):

            print(
                f"{index:02} | "
                f"{str(block.get('status', '')):10} | "
                f"{str(block.get('translator', '')):7} | "
                f"{block.get('text', '')}"
            )

            print(
                f"   => "
                f"{block.get('translated_text', '')}"
            )

        # =================================================
        # 3/4 Layout
        # =================================================

        print()
        print(
            "[3/4] Layout..."
        )

        layouts = self.prepare_layout(
            translated_blocks
        )

        valid_layouts = sum(
            1
            for item in layouts
            if item.get(
                "layout",
                {}
            ).get(
                "valid",
                False,
            )
        )

        print(
            f"Layouts: "
            f"{len(layouts)}"
        )

        print(
            f"Valid layouts: "
            f"{valid_layouts}"
        )

        # =================================================
        # 4/4 Rendering
        # =================================================

        print()
        print(
            "[4/4] Rendering..."
        )

        final_image, mask = self.render(
            image,
            translated_blocks,
        )

        # -------------------------------------------------
        # Save
        # -------------------------------------------------

        final_image.save(
            output_path,
            quality=95,
        )

        # -------------------------------------------------
        # Done
        # -------------------------------------------------

        print()
        print("=" * 70)
        print("DONE")
        print(
            f"Output: "
            f"{output_path}"
        )
        print("=" * 70)

        return {
            "input":
                str(input_path),

            "output":
                str(output_path),

            "ocr_blocks":
                ocr_blocks,

            "translations":
                translated_blocks,

            "layouts":
                layouts,

            "mask":
                mask,

            "image":
                final_image,
        }