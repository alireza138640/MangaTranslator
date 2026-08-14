from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QApplication,
    QMenu
)

from PySide6.QtCore import Qt

from ui.themes import toggle_theme



class Toolbar(QWidget):

    def __init__(self):

        super().__init__()

        self.setup_ui()



    def setup_ui(self):

        self.setFixedHeight(
            60
        )


        layout = QHBoxLayout()


        layout.setContentsMargins(
            20,
            5,
            20,
            5
        )


        layout.setSpacing(
            10
        )



        # Logo

        self.logo = QLabel(
            "🈶 Manga Translator AI"
        )


        self.logo.setAlignment(
            Qt.AlignCenter
        )



        # Open Button

        self.open_button = QPushButton(
            "📂 Open Manga"
        )


        self.open_button.setFixedSize(
            140,
            38
        )



        # Menu

        menu = QMenu(
            self
        )


        self.open_image_action = menu.addAction(
            "🖼 Open Images"
        )


        self.open_folder_action = menu.addAction(
            "📁 Open Folder"
        )


        self.open_archive_action = menu.addAction(
            "📦 Open ZIP / CBZ"
        )


        self.open_button.setMenu(
            menu
        )



        # Theme

        self.theme_button = QPushButton(
            "🌙"
        )


        self.theme_button.setFixedSize(
            45,
            38
        )



        # Layout

        layout.addWidget(
            self.logo
        )


        layout.addStretch()


        layout.addWidget(
            self.open_button
        )


        layout.addWidget(
            self.theme_button
        )



        self.setLayout(
            layout
        )



        # Theme Event

        self.theme_button.clicked.connect(
        lambda:
        toggle_theme(
            QApplication.instance(),
            self.theme_button
         )
        )