from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QPushButton,
    QLabel
)


class PageControls(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()


    def setup_ui(self):

        layout = QHBoxLayout()


        self.previous_button = QPushButton(
            "◀ Previous"
        )


        self.page_label = QLabel(
            "0 / 0"
        )


        self.page_label.setMinimumWidth(
            80
        )


        self.next_button = QPushButton(
            "Next ▶"
        )


        layout.addWidget(
            self.previous_button
        )


        layout.addStretch()


        layout.addWidget(
            self.page_label
        )


        layout.addStretch()


        layout.addWidget(
            self.next_button
        )


        self.setLayout(
            layout
        )



    def set_page_info(self, current, total):

        self.page_label.setText(
            f"{current} / {total}"
        )