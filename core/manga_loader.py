import os
import zipfile
import shutil


class MangaLoader:

    def __init__(self):

        self.temp_folder = "temp_manga"


    def load(self, path):

        if path.lower().endswith(
            (
                ".zip",
                ".cbz"
            )
        ):

            return self.load_archive(
                path
            )


        elif path.lower().endswith(
            (
                ".png",
                ".jpg",
                ".jpeg",
                ".webp"
            )
        ):

            return [
                os.path.abspath(path)
            ]


        elif os.path.isdir(path):

            return self.load_folder(
                path
            )


        else:

            raise Exception(
                "Unsupported file type"
            )



    def load_archive(self, path):

        if os.path.exists(
            self.temp_folder
        ):

            shutil.rmtree(
                self.temp_folder
            )


        os.makedirs(
            self.temp_folder
        )


        with zipfile.ZipFile(
            path,
            "r"
        ) as archive:

            archive.extractall(
                self.temp_folder
            )


        return self.find_images(
            self.temp_folder
        )



    def load_folder(self, folder):

        return self.find_images(
            folder
        )



    def find_images(self, folder):

        images = []


        for root, dirs, files in os.walk(folder):

            for file in files:

                if file.lower().endswith(
                    (
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".webp"
                    )
                ):

                    images.append(
                        os.path.abspath(
                            os.path.join(
                                root,
                                file
                            )
                        )
                    )


        images.sort()


        return images