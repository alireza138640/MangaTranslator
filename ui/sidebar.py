from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea
)

from PySide6.QtCore import (
    Qt,
    Signal,
    QSize
)

from PySide6.QtGui import (
    QPixmap,
    QIcon
)


class Sidebar(QWidget):

    page_selected = Signal(int)

    def __init__(self):
        super().__init__()

        self.pages = []
        self.buttons = []
        self.current_page = 0

        self.setup_ui()



    def setup_ui(self):

        self.setFixedWidth(
            180
        )


        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        main_layout.setSpacing(
            8
        )


        # Title

        self.title = QLabel(
            "Pages"
        )

        self.title.setAlignment(
            Qt.AlignCenter
        )

        self.title.setFixedHeight(
            30
        )

        main_layout.addWidget(
            self.title
        )


        # Scroll Area

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        self.scroll_area.setFrameShape(
            QScrollArea.NoFrame
        )


        # Container

        self.container = QWidget()


        self.pages_layout = QVBoxLayout()

        self.pages_layout.setContentsMargins(
            4,
            4,
            4,
            4
        )

        self.pages_layout.setSpacing(
            10
        )

        self.pages_layout.setAlignment(
            Qt.AlignTop
        )


        self.container.setLayout(
            self.pages_layout
        )


        self.scroll_area.setWidget(
            self.container
        )


        main_layout.addWidget(
            self.scroll_area,
            1
        )


        self.setLayout(
            main_layout
        )



    def load_pages(
        self,
        pages
    ):

        self.pages = list(
            pages
        )

        self.current_page = 0


        # Remove old thumbnails

        for button in self.buttons:

            button.deleteLater()


        self.buttons.clear()


        # Create thumbnails

        for index, path in enumerate(
            self.pages
        ):

            button = QPushButton()

            button.setFixedSize(
                145,
                175
            )

            button.setCheckable(
                True
            )

            button.setCursor(
                Qt.PointingHandCursor
            )


            # Normal / Selected style

            button.setStyleSheet(
                """
                QPushButton {
                    background: transparent;
                    border: none;
                    border-left: 4px solid transparent;
                    border-radius: 6px;
                    padding-left: 4px;
                }

                QPushButton:hover {
                    background: rgba(255, 255, 255, 20);
                }

                QPushButton:checked {
                    background: rgba(40, 120, 255, 25);
                    border-left: 4px solid #2F80FF;
                }
                """
            )


            pixmap = QPixmap(
                path
            )


            if not pixmap.isNull():

                pixmap = pixmap.scaled(
                    125,
                    145,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                button.setIcon(
                    QIcon(
                        pixmap
                    )
                )

                button.setIconSize(
                    QSize(
                        125,
                        145
                    )
                )

            else:

                button.setText(
                    "❌"
                )


            button.setToolTip(
                f"Page {index + 1}"
            )


            button.clicked.connect(
                lambda checked=False, i=index:
                self.on_page_clicked(i)
            )


            self.pages_layout.addWidget(
                button
            )

            self.buttons.append(
                button
            )


        if self.buttons:

            self.select_page(
                0
            )



    def on_page_clicked(
        self,
        index
    ):

        if (
            index < 0
            or index >= len(self.buttons)
        ):
            return


        self.current_page = index


        self.select_page(
            index
        )


        self.page_selected.emit(
            index
        )



    def select_page(
        self,
        index
    ):

        if (
            index < 0
            or index >= len(self.buttons)
        ):
            return


        self.current_page = index


        for i, button in enumerate(
            self.buttons
        ):

            button.setChecked(
                i == index
            )


        self.scroll_area.ensureWidgetVisible(
            self.buttons[index]
        )