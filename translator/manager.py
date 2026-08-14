from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .cache import TranslationCache
from .online import OnlineTranslator
from .offline import OfflineTranslator


# =====================================================
# TRANSLATION BLOCK
# =====================================================

@dataclass
class TranslationBlock:

    source_text: str
    translated_text: str

    source_language: str = "en"
    target_language: str = "fa"

    box: Optional[List[int]] = None

    confidence: float = 0.0

    status: str = "translated"

    translator: str = "unknown"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# =====================================================
# TRANSLATION MANAGER
# =====================================================

class TranslationManager:

    def __init__(
        self,
        source_language="en",
        target_language="fa",
        mode="auto",
    ):

        self.source_language = source_language
        self.target_language = target_language
        self.mode = mode

        self.cache = TranslationCache()

        self.online = OnlineTranslator(
            source_language=source_language,
            target_language=target_language,
        )

        # NLLB is the primary offline engine.
        # Argos remains the fallback inside OfflineTranslator.
        self.offline = OfflineTranslator(
            source_language=source_language,
            target_language=target_language,
            engine="nllb",
        )

    # =====================================================
    # GENERIC GETTER
    # =====================================================

    def _get(
        self,
        block,
        key,
        default=None,
    ):

        if isinstance(block, dict):

            return block.get(
                key,
                default,
            )

        return getattr(
            block,
            key,
            default,
        )

    # =====================================================
    # TRANSLATE ONE BLOCK
    # =====================================================

    def translate_block(self, block):

        source_text = self._get(
            block,
            "text",
            "",
        )

        if not source_text:

            source_text = self._get(
                block,
                "source_text",
                "",
            )

        source_text = str(
            source_text or ""
        ).strip()

        if not source_text:

            return self._empty_result(
                block
            )

        box = self._get(
            block,
            "box",
            None,
        )

        confidence = self._get(
            block,
            "confidence",
            0.0,
        )

        # =================================================
        # CACHE
        # =================================================

        cached = self.cache.get(
            source_text,
            self.source_language,
            self.target_language,
        )

        if cached:

            return TranslationBlock(
                source_text=source_text,
                translated_text=cached,
                source_language=self.source_language,
                target_language=self.target_language,
                box=box,
                confidence=confidence,
                status="cached",
                translator="cache",
            )

        # =================================================
        # TRANSLATION
        # =================================================

        translated_text = None
        translator_name = "unknown"

        # =================================================
        # ONLINE
        # =================================================

        if self.mode in (
            "auto",
            "online",
        ):

            try:

                translated_text = (
                    self.online.translate(
                        source_text
                    )
                )

                if translated_text:

                    translator_name = "online"

            except Exception as exc:

                print(
                    f"[Translation] "
                    f"Online failed: {exc}"
                )

                if self.mode == "online":

                    raise

        # =================================================
        # OFFLINE
        # =================================================

        if not translated_text:

            try:

                translated_text = (
                    self.offline.translate(
                        source_text
                    )
                )

                translator_name = (
                    self.offline.engine
                )

            except Exception as exc:

                raise RuntimeError(
                    "Translation failed for: "
                    f"{source_text}\n"
                    f"Reason: {exc}"
                ) from exc

        # =================================================
        # SAVE CACHE
        # =================================================

        self.cache.set(
            source_text,
            self.source_language,
            self.target_language,
            translated_text,
        )

        return TranslationBlock(
            source_text=source_text,
            translated_text=translated_text,
            source_language=self.source_language,
            target_language=self.target_language,
            box=box,
            confidence=confidence,
            status="translated",
            translator=translator_name,
            metadata={
                "engine": translator_name,
            },
        )

    # =====================================================
    # TRANSLATE MANY BLOCKS
    # =====================================================

    def translate_blocks(self, blocks):

        results = []

        for block in blocks:

            results.append(
                self.translate_block(
                    block
                )
            )

        return results

    # =====================================================
    # EMPTY RESULT
    # =====================================================

    def _empty_result(self, block):

        return TranslationBlock(
            source_text="",
            translated_text="",
            source_language=self.source_language,
            target_language=self.target_language,
            box=self._get(
                block,
                "box",
                None,
            ),
            confidence=self._get(
                block,
                "confidence",
                0.0,
            ),
            status="empty",
            translator="none",
        )


# =====================================================
# TRANSLATION BLOCK -> DICT
# =====================================================

def translation_block_to_dict(block):

    return {
        "source_text": block.source_text,
        "translated_text": block.translated_text,
        "source_language": block.source_language,
        "target_language": block.target_language,
        "box": block.box,
        "confidence": block.confidence,
        "status": block.status,
        "translator": block.translator,
        "metadata": block.metadata,
    }