class OCRResult:

    def __init__(
        self,
        text,
        x,
        y,
        width,
        height,
        confidence,
        polygon=None
    ):

        self.text = text

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.confidence = confidence

        self.polygon = polygon

    def to_dict(self):

        data = {
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "confidence": self.confidence,
        }

        if self.polygon is not None:
            data["polygon"] = self.polygon

        return data