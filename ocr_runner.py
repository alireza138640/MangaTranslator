import sys
import traceback
from pathlib import Path


def configure_console():

    # -----------------------------------------
    # Windows UTF-8 console
    # -----------------------------------------

    try:

        if hasattr(
            sys.stdout,
            "reconfigure",
        ):

            sys.stdout.reconfigure(
                encoding="utf-8",
                errors="replace",
            )

    except Exception:
        pass

    try:

        if hasattr(
            sys.stderr,
            "reconfigure",
        ):

            sys.stderr.reconfigure(
                encoding="utf-8",
                errors="replace",
            )

    except Exception:
        pass


def safe_print(
    *args,
    **kwargs,
):

    try:

        print(
            *args,
            **kwargs,
        )

    except UnicodeEncodeError:

        # -----------------------------------------
        # Fallback for old Windows console
        # -----------------------------------------

        text = " ".join(
            str(arg)
            for arg in args
        )

        end = kwargs.get(
            "end",
            "\n",
        )

        try:

            sys.stdout.buffer.write(
                (
                    text
                    + end
                ).encode(
                    "utf-8",
                    errors="replace",
                )
            )

            sys.stdout.flush()

        except Exception:

            try:

                sys.stdout.write(
                    "[Unicode output omitted]\n"
                )

            except Exception:
                pass


def main():

    configure_console()

    # -----------------------------------------
    # Arguments
    # -----------------------------------------

    if len(sys.argv) < 3:

        safe_print(
            "Usage: python ocr_runner.py "
            "<input_image> <output_image> "
            "[source_language] [target_language]"
        )

        return 1

    input_path = Path(
        sys.argv[1]
    ).resolve()

    output_path = Path(
        sys.argv[2]
    ).resolve()

    source_language = (
        sys.argv[3]
        if len(sys.argv) > 3
        else "en"
    )

    target_language = (
        sys.argv[4]
        if len(sys.argv) > 4
        else "fa"
    )

    # -----------------------------------------
    # Header
    # -----------------------------------------

    safe_print(
        "=" * 70
    )

    safe_print(
        "MangaTranslator OCR Runner"
    )

    safe_print(
        "=" * 70
    )

    safe_print(
        f"Input : {input_path}"
    )

    safe_print(
        f"Output: {output_path}"
    )

    safe_print(
        f"Source: {source_language}"
    )

    safe_print(
        f"Target: {target_language}"
    )

    safe_print()

    # -----------------------------------------
    # Input validation
    # -----------------------------------------

    if not input_path.exists():

        safe_print(
            "ERROR: Input image not found:"
        )

        safe_print(
            str(input_path)
        )

        return 2

    # -----------------------------------------
    # Output directory
    # -----------------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------
    # Pipeline
    # -----------------------------------------

    try:

        from renderer.pipeline import (
            MangaRendererPipeline
        )

        pipeline = MangaRendererPipeline(
            source_language=source_language,
            target_language=target_language,
            translation_mode="offline",
        )

        result = pipeline.process_page(
            str(input_path),
            str(output_path),
        )

        # -----------------------------------------
        # Verify output
        # -----------------------------------------

        if not output_path.exists():

            safe_print()

            safe_print(
                "ERROR: Pipeline finished "
                "but output file was not created."
            )

            return 3

        # -----------------------------------------
        # Success
        # -----------------------------------------

        safe_print()

        safe_print(
            "=" * 70
        )

        safe_print(
            "OCR PIPELINE COMPLETED"
        )

        safe_print(
            "=" * 70
        )

        safe_print(
            f"Output: {output_path}"
        )

        safe_print(
            f"OCR blocks: "
            f"{len(result.get('ocr_blocks', []))}"
        )

        safe_print(
            f"Translations: "
            f"{len(result.get('translations', []))}"
        )

        safe_print(
            f"Layouts: "
            f"{len(result.get('layouts', []))}"
        )

        safe_print(
            "=" * 70
        )

        return 0

    except Exception as error:

        # -----------------------------------------
        # Error
        # -----------------------------------------

        safe_print()

        safe_print(
            "=" * 70
        )

        safe_print(
            "OCR PIPELINE ERROR"
        )

        safe_print(
            "=" * 70
        )

        safe_print(
            f"Error type: "
            f"{type(error).__name__}"
        )

        safe_print(
            f"Error: "
            f"{error}"
        )

        safe_print(
            "=" * 70
        )

        safe_print()

        safe_print(
            "TRACEBACK:"
        )

        try:

            traceback.print_exc()

        except Exception:

            pass

        return 10


if __name__ == "__main__":

    sys.exit(
        main()
    )