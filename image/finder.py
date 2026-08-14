from pathlib import Path


class ImageFinder:

    SUPPORTED_EXTENSIONS = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    ]

    def __init__(self):
        self.input_folder = Path("input")

    def find_images(self):

        images = []

        for file in self.input_folder.iterdir():

            if file.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                images.append(file)

        return sorted(images)