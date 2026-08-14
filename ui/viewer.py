from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton
)

from PySide6.QtCore import (
    Qt,
    Signal
)

from PySide6.QtGui import QPixmap

import os



class Viewer(QWidget):

    page_changed = Signal(int)


    def __init__(self):

        super().__init__()

        self.pages = []

        self.current_page = 0

        self.setup_ui()

        self.setFocusPolicy(
            Qt.StrongFocus
        )



    def setup_ui(self):

        layout = QVBoxLayout()


        layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        layout.setSpacing(
            8
        )


        # Image Viewer

        self.image_label = QLabel(
            "📖 Manga Preview"
        )

        self.image_label.setAlignment(
            Qt.AlignCenter
        )


        self.image_label.setMinimumSize(
            300,
            300
        )


        layout.addWidget(
            self.image_label,
            1
        )



        # Controls

        controls = QHBoxLayout()

        controls.setSpacing(
            10
        )


        self.previous_button = QPushButton(
            "◀"
        )

        self.previous_button.setFixedSize(
            45,
            35
        )



        self.page_label = QLabel(
            "0 / 0"
        )


        self.page_label.setAlignment(
            Qt.AlignCenter
        )


        self.page_label.setMinimumWidth(
            100
        )



        self.next_button = QPushButton(
            "▶"
        )


        self.next_button.setFixedSize(
            45,
            35
        )



        controls.addStretch()


        controls.addWidget(
            self.previous_button
        )


        controls.addWidget(
            self.page_label
        )


        controls.addWidget(
            self.next_button
        )


        controls.addStretch()



        layout.addLayout(
            controls
        )


        self.setLayout(
            layout
        )



        # Button Style

        button_style = """

        QPushButton {

            background-color: #2b2b2b;

            color: white;

            border-radius: 8px;

            font-size: 16px;

        }


        QPushButton:hover {

            background-color: #2F80FF;

        }


        QPushButton:pressed {

            background-color: #1F5CCC;

        }

        """


        self.previous_button.setStyleSheet(
            button_style
        )


        self.next_button.setStyleSheet(
            button_style
        )



        # Connections

        self.previous_button.clicked.connect(
            self.previous_page
        )


        self.next_button.clicked.connect(
            self.next_page
        )



    def load_pages(
        self,
        pages
    ):

        self.pages = list(
            pages
        )


        self.current_page = 0


        self.show_current_page()



    def show_page(
        self,
        index
    ):

        if not self.pages:

            return


        if index < 0 or index >= len(self.pages):

            return


        self.current_page = index


        self.show_current_page()



    def show_current_page(self):

        if not self.pages:

            return



        path = self.pages[
            self.current_page
        ]



        if not os.path.exists(
            path
        ):

            self.image_label.setText(
                "❌ File Not Found"
            )

            return



        pixmap = QPixmap(
            path
        )



        if pixmap.isNull():

            self.image_label.setText(
                "❌ Cannot load image"
            )

            return



        pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )


        self.image_label.setPixmap(
            pixmap
        )


        self.page_label.setText(
            f"{self.current_page + 1} / {len(self.pages)}"
        )



    def next_page(self):

        if not self.pages:

            return



        if self.current_page < len(self.pages) - 1:

            self.current_page += 1


            self.show_current_page()


            self.page_changed.emit(
                self.current_page
            )



    def previous_page(self):

        if not self.pages:

            return



        if self.current_page > 0:

            self.current_page -= 1


            self.show_current_page()


            self.page_changed.emit(
                self.current_page
            )



    def keyPressEvent(
        self,
        event
    ):

        key = event.key()


        if key == Qt.Key_Right:

            self.next_page()

            return



        if key == Qt.Key_Left:

            self.previous_page()

            return



        if key == Qt.Key_PageDown:

            self.next_page()

            return



        if key == Qt.Key_PageUp:

            self.previous_page()

            return



        super().keyPressEvent(
            event
        )



    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
        )


        if self.pages:

            self.show_current_page()