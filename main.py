import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow

from ui.themes import load_theme



def start():

    app = QApplication(
        sys.argv
    )


    load_theme(
        app,
        "dark"
    )


    window = MainWindow()

    window.show()


    sys.exit(
        app.exec()
    )



if __name__ == "__main__":

    start()