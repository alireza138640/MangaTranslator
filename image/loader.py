from pathlib import Path
from PIL import Image


class ImageLoader:

    def __init__(self):
        self.input_folder = Path("input")

    def load(self, filename):
        file_path = self.input_folder / filename

        if not file_path.exists():
            raise FileNotFoundError(f"{filename} پیدا نشد.")

        image = Image.open(file_path)

        return image