import re
from typing import List, Dict, Any


# =========================================================
# Validation rules
# =========================================================

COMMON_WORDS = {
    "A", "I", "AN", "AND", "ARE", "AS", "AT", "BE", "BUT",
    "BY", "CAN", "CRAZY", "DO", "DID", "FOR", "FROM", "HAVE",
    "HE", "HER", "HERE", "HIS", "HOW", "I'M", "IF", "IN", "IS",
    "ISN'T", "IT", "ITS", "IT'S", "LIKE", "LOOKS", "MATCH",
    "ME", "MY", "NOT", "OF", "ON", "OR", "SO", "THAT", "THE",
    "THEY", "THIS", "TO", "US", "WAS", "WHAT", "WHEN", "WHY",
    "WILL", "WITH", "WOULD", "YOU", "YEP",
}


# =========================================================
# Suspicious token detection
# =========================================================

def find_suspicious_tokens(
    text: str,
) -> List[Dict[str, Any]]:

    candidates = []

    if not text:
        return candidates

    tokens = re.findall(
        r"[A-Za-z]+(?:'[A-Za-z]+)?",
        text,
    )

    for token in tokens:

        normalized = token.upper()

        # -----------------------------------------
        # تک‌حرفی‌های مشکوک
        # -----------------------------------------

        if len(normalized) == 1:

            if normalized not in {"A", "I"}:

                candidates.append({
                    "token": token,
                    "reason": "single_letter",
                })

            continue

        # -----------------------------------------
        # کلمات بسیار کوتاه ناشناخته
        # -----------------------------------------

        if (
            len(normalized) <= 2
            and normalized not in COMMON_WORDS
        ):

            candidates.append({
                "token": token,
                "reason": "unknown_short_token",
            })

    return candidates


# =========================================================
# Sentence-level validation
# =========================================================

def validate_text(
    text: str,
) -> List[Dict[str, Any]]:
    """
    بررسی زبانی سطح پایه.

    هیچ تغییری در متن ایجاد نمی‌کند.
    """

    issues = []

    if not text or not text.strip():

        issues.append({
            "reason": "empty_text",
        })

        return issues

    suspicious = find_suspicious_tokens(
        text
    )

    for item in suspicious:

        issues.append({
            "reason": item["reason"],
            "token": item["token"],
        })

    # -----------------------------------------
    # فاصله‌های غیرعادی
    # -----------------------------------------

    if re.search(
        r"\s{2,}",
        text,
    ):

        issues.append({
            "reason": "multiple_spaces",
        })

    # -----------------------------------------
    # علائم نگارشی تکراری غیرمعمول
    # -----------------------------------------

    if re.search(
        r"[!?]{4,}",
        text,
    ):

        issues.append({
            "reason": "excessive_punctuation",
        })

    return issues


# =========================================================
# Validate OCR blocks
# =========================================================

def validate_blocks(
    blocks,
):
    """
    بررسی OCRBlockها.

    متن اصلی دست‌نخورده باقی می‌ماند.
    فقط status و validation اطلاعات اضافه می‌شوند.
    """

    output = []

    for block in blocks:

        text = str(
            block.text
        ).strip()

        issues = validate_text(
            text
        )

        # ---------------------------------
        # ذخیره validation
        # ---------------------------------

        block.validation = {
            "valid": len(issues) == 0,
            "issues": issues,
        }

        # ---------------------------------
        # اگر مشکل زبانی پیدا شد
        # ---------------------------------

        if issues:

            block.status = "review"

        # ---------------------------------
        # confidence پایین
        # ---------------------------------

        elif block.confidence < 0.85:

            block.status = "review"

        else:

            block.status = "accepted"

        output.append(block)

    return output


# =========================================================
# Print validation report
# =========================================================

def print_validation_report(
    blocks,
):

    print()
    print("=" * 70)
    print("OCR VALIDATION")
    print("=" * 70)

    review_count = 0

    for block in blocks:

        validation = getattr(
            block,
            "validation",
            {},
        )

        issues = validation.get(
            "issues",
            [],
        )

        print(
            f"{block.id:02d} | "
            f"{block.status:<8} | "
            f"conf={block.confidence:.3f}"
        )

        print(
            f"    {block.text}"
        )

        if issues:

            review_count += 1

            for issue in issues:

                reason = issue.get(
                    "reason",
                    "unknown",
                )

                token = issue.get(
                    "token"
                )

                if token:

                    print(
                        f"    -> {reason}: {token}"
                    )

                else:

                    print(
                        f"    -> {reason}"
                    )

    print("-" * 70)

    print(
        f"Blocks: {len(blocks)} | "
        f"Review: {review_count} | "
        f"Accepted: "
        f"{len(blocks) - review_count}"
    )

    print("=" * 70)