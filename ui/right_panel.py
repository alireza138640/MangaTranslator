from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QGroupBox,
    QProgressBar
)

from PySide6.QtCore import Qt, Signal



class RightPanel(QWidget):

    translate_requested = Signal(
        str,
        str,
        str
    )


    def __init__(self):

        super().__init__()

        self.current_page = None

        self.setup_ui()



    def setup_ui(self):

        self.setFixedWidth(
            250
        )


        layout = QVBoxLayout()


        layout.setContentsMargins(
            10,
            10,
            10,
            10
        )


        layout.setSpacing(
            12
        )


        self.title = QLabel(
            "⚙ Translation"
        )


        self.title.setAlignment(
            Qt.AlignCenter
        )


        layout.addWidget(
            self.title
        )



        language_box = QGroupBox(
            "Languages"
        )


        language_layout = QVBoxLayout()



        self.source_language = QComboBox()

        self.source_language.addItems(
            [
                "Japanese 🇯🇵",
                "Korean 🇰🇷",
                "English 🇺🇸"
            ]
        )



        self.target_language = QComboBox()

        self.target_language.addItems(
            [
                "Persian 🇮🇷",
                "English 🇺🇸",
                "Arabic 🇸🇦"
            ]
        )



        language_layout.addWidget(
            QLabel("Source")
        )


        language_layout.addWidget(
            self.source_language
        )


        language_layout.addWidget(
            QLabel("Target")
        )


        language_layout.addWidget(
            self.target_language
        )


        language_box.setLayout(
            language_layout
        )


        layout.addWidget(
            language_box
        )



        self.translate_button = QPushButton(
            "🌐 Translate"
        )


        self.translate_button.setFixedHeight(
            40
        )


        layout.addWidget(
            self.translate_button
        )



        self.progress = QProgressBar()


        layout.addWidget(
            self.progress
        )



        self.status = QLabel(
            "Ready"
        )


        self.status.setAlignment(
            Qt.AlignCenter
        )


        layout.addWidget(
            self.status
        )


        layout.addStretch()


        self.setLayout(
            layout
        )



        self.translate_button.clicked.connect(
            self.request_translate
        )



    def set_page(
        self,
        path
    ):

        self.current_page = path


        self.status.setText(
            "Page Selected"
        )



    def request_translate(self):

        if not self.current_page:

            self.status.setText(
                "❌ No page selected"
            )

            return



        self.translate_requested.emit(
            self.current_page,
            self.source_language.currentText(),
            self.target_language.currentText()
        )