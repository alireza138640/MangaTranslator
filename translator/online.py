class OnlineTranslator:

    def __init__(
        self,
        source_language="en",
        target_language="fa",
    ):

        self.source_language = source_language
        self.target_language = target_language

    def translate(self, text):

        raise NotImplementedError(
            "Online translator is not connected yet."
        )