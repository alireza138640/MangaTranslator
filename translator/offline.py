import re

# =====================================================
# OPTIONAL IMPORTS
# =====================================================

try:
    import torch

    TORCH_AVAILABLE = True

except ImportError:
    torch = None
    TORCH_AVAILABLE = False


try:
    from transformers import (
        AutoTokenizer,
        AutoModelForSeq2SeqLM,
    )

    TRANSFORMERS_AVAILABLE = True

except ImportError:
    AutoTokenizer = None
    AutoModelForSeq2SeqLM = None
    TRANSFORMERS_AVAILABLE = False


try:
    import argostranslate.translate

    ARGOS_AVAILABLE = True

except ImportError:
    ARGOS_AVAILABLE = False


# =====================================================
# NLLB CONFIG
# =====================================================

NLLB_MODEL = "facebook/nllb-200-distilled-600M"

NLLB_LANGUAGE_CODES = {
    "en": "eng_Latn",
    "fa": "pes_Arab",
}


class OfflineTranslator:

    def __init__(
        self,
        source_language="en",
        target_language="fa",
        engine="nllb",
    ):

        self.source_language = source_language
        self.target_language = target_language

        # Requested engine.
        #
        # nllb = NLLB first, Argos fallback
        # argos = Argos only
        self.requested_engine = engine.lower()

        self.engine = "NLLB-200"

        # NLLB objects are loaded lazily.
        self._tokenizer = None
        self._model = None
        self._device = None

        self._nllb_loaded = False
        self._nllb_error = None

    # =====================================================
    # STATUS
    # =====================================================

    def status(self):

        nllb_available = (
            TORCH_AVAILABLE
            and TRANSFORMERS_AVAILABLE
            and self._languages_supported_by_nllb()
        )

        cuda_available = (
            TORCH_AVAILABLE
            and torch.cuda.is_available()
        )

        argos_available = self._argos_status()

        if self.requested_engine == "argos":

            available = argos_available
            engine = "Argos Translate"

        else:

            available = (
                nllb_available
                or argos_available
            )

            engine = "NLLB-200"

        return {
            "available": available,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "engine": engine,
            "nllb_available": nllb_available,
            "nllb_loaded": self._nllb_loaded,
            "nllb_error": self._nllb_error,
            "argos_available": argos_available,
            "cuda_available": cuda_available,
            "device": (
                str(self._device)
                if self._device
                else (
                    "cuda"
                    if cuda_available
                    else "cpu"
                )
            ),
        }

    # =====================================================
    # ARGOS STATUS
    # =====================================================

    def _argos_status(self):

        if not ARGOS_AVAILABLE:
            return False

        try:

            languages = (
                argostranslate.translate
                .get_installed_languages()
            )

            source = next(
                (
                    language
                    for language in languages
                    if language.code == self.source_language
                ),
                None,
            )

            target = next(
                (
                    language
                    for language in languages
                    if language.code == self.target_language
                ),
                None,
            )

            if not source or not target:
                return False

            try:

                translation = (
                    source.get_translation(target)
                )

                return translation is not None

            except Exception:

                return False

        except Exception:

            return False

    # =====================================================
    # NLLB LANGUAGE SUPPORT
    # =====================================================

    def _languages_supported_by_nllb(self):

        return (
            self.source_language in NLLB_LANGUAGE_CODES
            and self.target_language in NLLB_LANGUAGE_CODES
        )

    # =====================================================
    # NLLB LANGUAGE CODE
    # =====================================================

    def _nllb_source_code(self):

        try:
            return NLLB_LANGUAGE_CODES[
                self.source_language
            ]

        except KeyError as exc:

            raise RuntimeError(
                "NLLB does not support source language "
                f"'{self.source_language}'."
            ) from exc

    def _nllb_target_code(self):

        try:
            return NLLB_LANGUAGE_CODES[
                self.target_language
            ]

        except KeyError as exc:

            raise RuntimeError(
                "NLLB does not support target language "
                f"'{self.target_language}'."
            ) from exc

    # =====================================================
    # LOAD NLLB
    # =====================================================

    def _load_nllb(self):

        if self._nllb_loaded:
            return

        if not TORCH_AVAILABLE:

            raise RuntimeError(
                "PyTorch is not installed."
            )

        if not TRANSFORMERS_AVAILABLE:

            raise RuntimeError(
                "Transformers is not installed."
            )

        if not self._languages_supported_by_nllb():

            raise RuntimeError(
                "NLLB language mapping is not available "
                f"for {self.source_language} -> "
                f"{self.target_language}."
            )

        print(
            "[NLLB] Loading model..."
        )

        try:

            self._device = (
                torch.device("cuda")
                if torch.cuda.is_available()
                else torch.device("cpu")
            )

            self._tokenizer = (
                AutoTokenizer.from_pretrained(
                    NLLB_MODEL
                )
            )

            # Use FP16 on CUDA to reduce VRAM usage.
            if self._device.type == "cuda":

                self._model = (
                    AutoModelForSeq2SeqLM
                    .from_pretrained(
                        NLLB_MODEL,
                        dtype=torch.float16,
                    )
                )

            else:

                self._model = (
                    AutoModelForSeq2SeqLM
                    .from_pretrained(
                        NLLB_MODEL
                    )
                )

            self._model.to(self._device)

            self._model.eval()

            self._nllb_loaded = True
            self._nllb_error = None

            print(
                f"[NLLB] Model loaded on "
                f"{self._device}."
            )

        except Exception as exc:

            self._nllb_loaded = False
            self._nllb_error = str(exc)

            self._tokenizer = None
            self._model = None

            raise RuntimeError(
                f"NLLB model loading failed: {exc}"
            ) from exc

    # =====================================================
    # NORMALIZE
    # =====================================================

    def _normalize(self, text):

        text = str(text or "").strip()

        if not text:
            return ""

        # OCR whitespace
        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        # OCR line-break hyphen
        text = re.sub(
            r"(?<=\w)-\s+",
            " ",
            text,
        )

        # Normalize repeated dots
        text = re.sub(
            r"\.{4,}",
            "...",
            text,
        )

        return text.strip()

    # =====================================================
    # MANGA GLOSSARY
    # =====================================================

    def _special_translation(self, text):

        normalized = text.lower().strip()

        special = {

            # Titles / chapter terminology

            "wriggling #30 shadow":
                "سایه پیچان شماره ۳۰",

            "#30 wriggling shadow":
                "سایه پیچان شماره ۳۰",

            # Common manga expressions

            "and so...":
                "و همین‌طور...",

            "so...":
                "پس...",
        }

        return special.get(normalized)

    # =====================================================
    # ARGOS
    # =====================================================

    def _argos_translate(self, text):

        if not ARGOS_AVAILABLE:

            raise RuntimeError(
                "Argos Translate is not installed."
            )

        try:

            translated = (
                argostranslate.translate.translate(
                    text,
                    self.source_language,
                    self.target_language,
                )
            )

        except Exception as exc:

            raise RuntimeError(
                f"Argos translation failed: {exc}"
            ) from exc

        return str(
            translated or ""
        ).strip()

    # =====================================================
    # NLLB
    # =====================================================

    def _nllb_translate(self, text):

        self._load_nllb()

        source_code = (
            self._nllb_source_code()
        )

        target_code = (
            self._nllb_target_code()
        )

        self._tokenizer.src_lang = source_code

        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        inputs = {
            key: value.to(self._device)
            for key, value in inputs.items()
        }

        target_token_id = (
            self._tokenizer
            .convert_tokens_to_ids(
                target_code
            )
        )

        with torch.inference_mode():

            generated_tokens = (
                self._model.generate(
                    **inputs,
                    forced_bos_token_id=target_token_id,
                    max_length=512,
                    num_beams=4,
                )
            )

        translated = (
            self._tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True,
            )[0]
        )

        return str(
            translated or ""
        ).strip()

    # =====================================================
    # QUALITY CHECK
    # =====================================================

    def _quality_score(
        self,
        original,
        translated,
    ):

        if not translated:
            return 0.0

        score = 1.0

        original = original.strip()
        translated = translated.strip()

        # ---------------------------------------------
        # Output still contains too much English
        # ---------------------------------------------

        english_chars = len(
            re.findall(
                r"[A-Za-z]",
                translated,
            )
        )

        total_letters = len(
            re.findall(
                r"[A-Za-zآ-ی]",
                translated,
            )
        )

        if total_letters > 0:

            english_ratio = (
                english_chars / total_letters
            )

            if english_ratio > 0.60:
                score -= 0.50

            elif english_ratio > 0.30:
                score -= 0.25

        # ---------------------------------------------
        # Translation is basically unchanged
        # ---------------------------------------------

        if translated.lower() == original.lower():

            score -= 0.70

        # ---------------------------------------------
        # Common broken output
        # ---------------------------------------------

        broken_patterns = [
            r"\bYOUR\b",
            r"\bYOU\b",
            r"\bTHE\b",
            r"\bAND\b",
            r"\bOF\b",
            r"\bTO\b",
        ]

        broken_count = sum(
            len(
                re.findall(
                    pattern,
                    translated,
                    flags=re.IGNORECASE,
                )
            )
            for pattern in broken_patterns
        )

        if broken_count >= 3:

            score -= 0.30

        return max(
            0.0,
            min(
                1.0,
                score,
            ),
        )

    # =====================================================
    # POST PROCESS
    # =====================================================

    def _post_process(
        self,
        original,
        translated,
    ):

        result = str(
            translated or ""
        ).strip()

        # Remove spaces before Persian punctuation

        result = re.sub(
            r"\s+([،؛؟!])",
            r"\1",
            result,
        )

        # Normalize three dots

        result = re.sub(
            r"\s*\.\s*\.\s*\.",
            "...",
            result,
        )

        # Normalize whitespace

        result = re.sub(
            r"\s+",
            " ",
            result,
        )

        return result.strip()

    # =====================================================
    # TRANSLATE
    # =====================================================

    def translate(self, text):

        text = self._normalize(text)

        if not text:
            return ""

        # ---------------------------------------------
        # Special manga terminology
        # ---------------------------------------------

        special = self._special_translation(
            text
        )

        if special:

            return special

        # ---------------------------------------------
        # Symbols / numbers only
        # ---------------------------------------------

        if re.fullmatch(
            r"[\d\s#.,!?…\-]+",
            text,
        ):

            return text

        translated = None

        # ---------------------------------------------
        # NLLB
        # ---------------------------------------------

        if self.requested_engine != "argos":

            try:

                translated = (
                    self._nllb_translate(
                        text
                    )
                )

                if translated:

                    self.engine = "NLLB-200"

            except Exception as exc:

                self._nllb_error = str(exc)

                print(
                    f"[NLLB] Translation failed: {exc}"
                )

                translated = None

        # ---------------------------------------------
        # Argos fallback
        # ---------------------------------------------

        if not translated:

            try:

                translated = (
                    self._argos_translate(
                        text
                    )
                )

                self.engine = "Argos Translate"

            except Exception as exc:

                raise RuntimeError(
                    "Both NLLB and Argos translation "
                    "failed.\n"
                    f"NLLB: {self._nllb_error}\n"
                    f"Argos: {exc}"
                ) from exc

        # ---------------------------------------------
        # Post processing
        # ---------------------------------------------

        translated = self._post_process(
            text,
            translated,
        )

        return translated

    # =====================================================
    # RELEASE MODEL
    # =====================================================

    def unload(self):

        self._model = None
        self._tokenizer = None
        self._nllb_loaded = False

        if (
            TORCH_AVAILABLE
            and torch.cuda.is_available()
        ):

            try:
                torch.cuda.empty_cache()

            except Exception:
                pass

        self._device = None