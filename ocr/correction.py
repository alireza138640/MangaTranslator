import re


# =========================================
# اصلاحات قطعی OCR
# =========================================

KNOWN_CORRECTIONS = {
    "sqz": "SO...",
    "sq2": "SO...",
    "so.": "SO...",
    "so": "SO...",
}


# =========================================
# اصلاح خطاهای شناخته‌شده در عبارت
# =========================================

PHRASE_CORRECTIONS = [
    (
        r"\bThe Old I Water Gate\.\.\.",
        "The Old Water Gate..."
    ),
]


# =========================================
# تشخیص متن مشکوک
# =========================================

def is_suspicious(text, confidence):
    text = text.strip()

    if not text:
        return False

    if confidence < 0.80:
        return True

    if len(text) <= 3:
        return True

    return False


# =========================================
# اصلاح یک متن
# =========================================

def correct_text(text, confidence=1.0):

    original = text.strip()

    if not original:
        return original

    key = original.lower().strip()

    # -------------------------------------
    # اصلاحات قطعی
    # -------------------------------------

    if key in KNOWN_CORRECTIONS:
        return KNOWN_CORRECTIONS[key]

    # -------------------------------------
    # اصلاح عبارت‌ها
    # -------------------------------------

    corrected = original

    for pattern, replacement in PHRASE_CORRECTIONS:

        corrected = re.sub(
            pattern,
            replacement,
            corrected,
            flags=re.IGNORECASE
        )

    # -------------------------------------
    # اصلاح حروف کوچک در متن مانگا
    #
    # فقط برای کلمات کوتاه و مشخص
    # -------------------------------------

    corrected = re.sub(
        r"\battacking us\b",
        "ATTACKING US",
        corrected,
        flags=re.IGNORECASE
    )

    return corrected


# =========================================
# اصلاح گروه‌ها
# =========================================

def correct_groups(groups):

    output = []

    for group in groups:

        text = group.get("text", "")

        confidence = float(
            group.get("confidence", 0.0)
        )

        corrected = correct_text(
            text,
            confidence
        )

        new_group = {
            **group,
            "text": corrected,
            "original_text": text,
        }

        output.append(new_group)

    return output


# =========================================
# پیدا کردن موارد مشکوک
# =========================================

def find_candidates(groups):

    candidates = []

    for index, group in enumerate(groups):

        text = group.get("text", "")

        confidence = float(
            group.get("confidence", 0.0)
        )

        if is_suspicious(text, confidence):

            candidates.append({
                "index": index,
                "text": text,
                "confidence": confidence,
                "reason": "suspicious_text",
                "box": group.get("box"),
            })

    return candidates


# =========================================
# چاپ موارد مشکوک
# =========================================

def print_candidates(groups):

    candidates = find_candidates(groups)

    print(
        f"Correction candidates: {len(candidates)}"
    )

    for candidate in candidates:

        print(
            f"[{candidate['index'] + 1}] "
            f"{candidate['text']} | "
            f"confidence="
            f"{candidate['confidence']:.3f} | "
            f"reason="
            f"{candidate['reason']} | "
            f"box="
            f"{candidate['box']}"
        )