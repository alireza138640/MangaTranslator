# ui/statusbar.py

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel
)


class StatusBar(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()



    def setup_ui(self):

        layout = QHBoxLayout()


        layout.setContentsMargins(
            10,
            5,
            10,
            5
        )


        self.status_label = QLabel(
            "🟢 Online"
        )


        layout.addWidget(
            self.status_label
        )


        self.setLayout(
            layout
        )



    def setText(self, text):

        self.status_label.setText(
            text
        )