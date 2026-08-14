from paddleocr import PaddleOCR
from PIL import Image, ImageDraw


IMAGE_PATH = "samples/page_001.jpeg"
OUTPUT_PATH = "samples/page_001_ocr_debug.jpg"


def main():
    print("Loading PaddleOCR...")

    ocr = PaddleOCR(lang="en")

    print("Running OCR...")
    results = ocr.predict(IMAGE_PATH)

    result = results[0]

    # ---------------------------------------------------------
    # IMPORTANT:
    # PaddleOCR may preprocess / unwarp the original image.
    # rec_polys are associated with the processed image.
    # Therefore we must draw boxes on output_img.
    # ---------------------------------------------------------

    doc_result = result.get("doc_preprocessor_res")

    if doc_result is not None and doc_result.get("output_img") is not None:
        print("Using PaddleOCR processed image for box visualization.")

        processed_img = doc_result["output_img"]

        # PaddleOCR returns a NumPy array.
        # Convert it to PIL.
        image = Image.fromarray(processed_img).convert("RGB")

    else:
        print("Processed image not available.")
        print("Falling back to original image.")

        image = Image.open(IMAGE_PATH).convert("RGB")

    draw = ImageDraw.Draw(image)

    rec_texts = result["rec_texts"]
    rec_polys = result["rec_polys"]
    rec_scores = result["rec_scores"]

    print()
    print("=" * 80)
    print(f"Detected text regions: {len(rec_texts)}")
    print(f"Visualization image size: {image.size}")
    print("=" * 80)

    for i, (text, poly, score) in enumerate(
        zip(rec_texts, rec_polys, rec_scores),
        start=1
    ):
        points = []

        for point in poly:
            x = int(point[0])
            y = int(point[1])

            points.append((x, y))

        # Draw OCR polygon
        draw.polygon(
            points,
            outline=(255, 0, 0),
            width=3
        )

        # Calculate label position
        x_values = [p[0] for p in points]
        y_values = [p[1] for p in points]

        min_x = min(x_values)
        min_y = min(y_values)

        # Label background
        label = f"{i}: {text}"

        # Draw label
        draw.text(
            (min_x, max(0, min_y - 18)),
            label,
            fill=(255, 0, 0)
        )

        print(
            f"{i:02d} | "
            f"{text:<25} | "
            f"confidence={score:.3f} | "
            f"box={points}"
        )

    image.save(
        OUTPUT_PATH,
        quality=95
    )

    print()
    print("=" * 80)
    print("OCR DEBUG IMAGE CREATED")
    print("=" * 80)
    print(f"Output: {OUTPUT_PATH}")
    print(f"Size:   {image.size}")
    print()


if __name__ == "__main__":
    main()