import hashlib
import json
from pathlib import Path


class TranslationCache:

    def __init__(self, cache_file=None):

        if cache_file is None:
            cache_file = (
                Path(__file__).resolve().parent
                / "translation_cache.json"
            )

        self.cache_file = Path(cache_file)

        self.data = {}

        self._load()

    # =====================================
    # ساخت کلید
    # =====================================

    def _make_key(
        self,
        text,
        source_language,
        target_language,
    ):

        raw = (
            f"{source_language}|"
            f"{target_language}|"
            f"{text.strip()}"
        )

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()

    # =====================================
    # Load
    # =====================================

    def _load(self):

        if not self.cache_file.exists():
            self.data = {}
            return

        try:

            with open(
                self.cache_file,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

                if isinstance(data, dict):
                    self.data = data
                else:
                    self.data = {}

        except (
            json.JSONDecodeError,
            OSError,
            TypeError,
        ):

            self.data = {}

    # =====================================
    # Save
    # =====================================

    def _save(self):

        self.cache_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_file = self.cache_file.with_suffix(
            ".tmp"
        )

        with open(
            temp_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.data,
                file,
                ensure_ascii=False,
                indent=2,
            )

        temp_file.replace(
            self.cache_file
        )

    # =====================================
    # Get
    # =====================================

    def get(
        self,
        text,
        source_language,
        target_language,
    ):

        key = self._make_key(
            text,
            source_language,
            target_language,
        )

        return self.data.get(key)

    # =====================================
    # Set
    # =====================================

    def set(
        self,
        text,
        source_language,
        target_language,
        translated_text,
    ):

        key = self._make_key(
            text,
            source_language,
            target_language,
        )

        self.data[key] = str(
            translated_text
        )

        self._save()

    # =====================================
    # Clear
    # =====================================

    def clear(self):

        self.data = {}

        if self.cache_file.exists():

            try:
                self.cache_file.unlink()

            except OSError:
                pass