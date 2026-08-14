import os
import sys
import subprocess

from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
)

from ui.toolbar import Toolbar
from ui.sidebar import Sidebar
from ui.viewer import Viewer
from ui.statusbar import StatusBar
from ui.right_panel import RightPanel

from core.manga_loader import MangaLoader


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.manga_loader = MangaLoader()

        self.pages = []

        self.project_root = (
            Path(__file__)
            .resolve()
            .parent
            .parent
        )

        self.ocr_python = (
            self.find_ocr_python()
        )

        self.setWindowTitle(
            "Manga Translator AI"
        )

        self.setFixedSize(
            1200,
            750
        )

        self.center_window()

        self.setup_ui()

    def find_ocr_python(self):

        candidates = [
            self.project_root
            / "ocrvenv"
            / "Scripts"
            / "python.exe",

            self.project_root
            / "ocr_venv"
            / "Scripts"
            / "python.exe",

            self.project_root
            / ".ocrvenv"
            / "Scripts"
            / "python.exe",

            self.project_root
            / ".ocr_venv"
            / "Scripts"
            / "python.exe",
        ]

        for python_path in candidates:

            if python_path.exists():

                return python_path

        return None

    def center_window(self):

        screen = self.screen().availableGeometry()

        x = (
            screen.width()
            - self.width()
        ) // 2

        y = (
            screen.height()
            - self.height()
        ) // 2

        self.move(
            x,
            y
        )

    def setup_ui(self):

        main_widget = QWidget()

        main_layout = QVBoxLayout()

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(
            0
        )

        # Toolbar

        self.toolbar = Toolbar()

        main_layout.addWidget(
            self.toolbar
        )

        # Center Layout

        center_layout = QHBoxLayout()

        center_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        center_layout.setSpacing(
            0
        )

        # Sidebar

        self.sidebar = Sidebar()

        center_layout.addWidget(
            self.sidebar
        )

        # Viewer

        self.viewer = Viewer()

        center_layout.addWidget(
            self.viewer,
            1
        )

        # Right Panel

        self.right_panel = RightPanel()

        center_layout.addWidget(
            self.right_panel
        )

        main_layout.addLayout(
            center_layout,
            1
        )

        # Status

        self.status_bar = StatusBar()

        main_layout.addWidget(
            self.status_bar
        )

        main_widget.setLayout(
            main_layout
        )

        self.setCentralWidget(
            main_widget
        )

        # Toolbar Connections

        self.toolbar.open_image_action.triggered.connect(
            self.open_images
        )

        self.toolbar.open_folder_action.triggered.connect(
            self.open_folder
        )

        self.toolbar.open_archive_action.triggered.connect(
            self.open_archive
        )

        # Sidebar

        self.sidebar.page_selected.connect(
            self.select_page
        )

        # Viewer

        self.viewer.page_changed.connect(
            self.sidebar.select_page
        )

        # Translate

        self.right_panel.translate_requested.connect(
            self.translate_page
        )

    def open_images(self):

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Manga Pages",
            "",
            "Images (*.png *.jpg *.jpeg *.webp)"
        )

        if not files:
            return

        self.pages = sorted(
            files
        )

        self.load_manga_pages()

    def open_folder(self):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Open Manga Folder"
        )

        if not folder:
            return

        self.pages = self.manga_loader.load(
            folder
        )

        self.load_manga_pages()

    def open_archive(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Manga Archive",
            "",
            "Archive (*.zip *.cbz)"
        )

        if not file_path:
            return

        self.pages = self.manga_loader.load(
            file_path
        )

        self.load_manga_pages()

    def load_manga_pages(self):

        if not self.pages:
            return

        self.viewer.load_pages(
            self.pages
        )

        self.sidebar.load_pages(
            self.pages
        )

        self.sidebar.select_page(
            0
        )

        self.right_panel.set_page(
            self.pages[0]
        )

        self.status_bar.setText(
            f"🟢 Loaded {len(self.pages)} Pages"
        )

    def select_page(
        self,
        index
    ):

        if not self.pages:
            return

        if index < 0 or index >= len(self.pages):
            return

        self.viewer.show_page(
            index
        )

        self.sidebar.select_page(
            index
        )

        self.right_panel.set_page(
            self.pages[index]
        )

    def get_language_code(
        self,
        language,
        target=False
    ):

        language_map = {
            "Japanese 🇯🇵": "ja",
            "Korean 🇰🇷": "ko",
            "English 🇺🇸": "en",
            "Persian 🇮🇷": "fa",
            "Arabic 🇸🇦": "ar",
        }

        return language_map.get(
            language,
            "fa" if target else "en"
        )

    def translate_page(
        self,
        page,
        source,
        target
    ):

        self.right_panel.status.setText(
            "🔍 Starting OCR..."
        )

        self.right_panel.progress.setValue(
            5
        )

        self.status_bar.setText(
            "🟡 Starting OCR pipeline..."
        )

        # -----------------------------------------
        # Check OCR environment
        # -----------------------------------------

        if self.ocr_python is None:

            self.right_panel.status.setText(
                "❌ ocrvenv not found"
            )

            self.status_bar.setText(
                "🔴 OCR environment not found"
            )

            print(
                "ERROR: OCR virtual environment "
                "was not found."
            )

            print(
                "Expected:"
            )

            print(
                self.project_root
                / "ocrvenv"
                / "Scripts"
                / "python.exe"
            )

            return

        # -----------------------------------------
        # Check runner
        # -----------------------------------------

        runner = (
            self.project_root
            / "ocr_runner.py"
        )

        if not runner.exists():

            self.right_panel.status.setText(
                "❌ ocr_runner.py not found"
            )

            self.status_bar.setText(
                "🔴 OCR runner not found"
            )

            print(
                f"ERROR: {runner}"
            )

            return

        # -----------------------------------------
        # Input
        # -----------------------------------------

        input_path = Path(
            page
        ).resolve()

        if not input_path.exists():

            self.right_panel.status.setText(
                "❌ Image not found"
            )

            print(
                f"ERROR: {input_path}"
            )

            return

        # -----------------------------------------
        # Output
        # -----------------------------------------

        output_dir = (
            self.project_root
            / "output"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path = (
            output_dir
            / f"{input_path.stem}_translated.png"
        )

        # -----------------------------------------
        # Languages
        # -----------------------------------------

        source_code = (
            self.get_language_code(
                source,
                target=False
            )
        )

        target_code = (
            self.get_language_code(
                target,
                target=True
            )
        )

        # -----------------------------------------
        # Command
        # -----------------------------------------

        command = [
            str(self.ocr_python),
            str(runner),
            str(input_path),
            str(output_path),
            source_code,
            target_code,
        ]

        print()
        print("=" * 70)
        print("Starting OCR subprocess")
        print("=" * 70)

        print(
            "Python:",
            self.ocr_python
        )

        print(
            "Runner:",
            runner
        )

        print(
            "Input:",
            input_path
        )

        print(
            "Output:",
            output_path
        )

        print(
            "Source:",
            source_code
        )

        print(
            "Target:",
            target_code
        )

        print("=" * 70)

        self.right_panel.progress.setValue(
            10
        )

        try:

            process = subprocess.run(
                command,
                cwd=str(
                    self.project_root
                ),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            print()
            print(
                process.stdout
            )

            if process.stderr:

                print()
                print(
                    "OCR STDERR:"
                )

                print(
                    process.stderr
                )

            # -------------------------------------
            # Failed
            # -------------------------------------

            if process.returncode != 0:

                self.right_panel.progress.setValue(
                    0
                )

                self.right_panel.status.setText(
                    "❌ OCR/Translation failed"
                )

                self.status_bar.setText(
                    "🔴 OCR pipeline failed"
                )

                print(
                    f"OCR process exited with "
                    f"code {process.returncode}"
                )

                return

            # -------------------------------------
            # Output check
            # -------------------------------------

            if not output_path.exists():

                self.right_panel.progress.setValue(
                    0
                )

                self.right_panel.status.setText(
                    "❌ Output not created"
                )

                self.status_bar.setText(
                    "🔴 Pipeline finished without output"
                )

                print(
                    "ERROR: Output file does not exist:"
                )

                print(
                    output_path
                )

                return

            # -------------------------------------
            # Success
            # -------------------------------------

            self.right_panel.progress.setValue(
                100
            )

            self.right_panel.status.setText(
                "✅ Translation completed"
            )

            self.status_bar.setText(
                f"🟢 Output: {output_path.name}"
            )

            print()
            print(
                "=" * 70
            )
            print(
                "OUTPUT CREATED"
            )
            print(
                output_path
            )
            print(
                "=" * 70
            )

            # -------------------------------------
            # Show translated image
            # -------------------------------------

            translated_path = str(
                output_path
            )

            current_index = (
                self.viewer.current_page
            )

            if (
                current_index is not None
                and
                0 <= current_index < len(
                    self.pages
                )
            ):

                self.pages[
                    current_index
                ] = translated_path

                self.viewer.pages[
                    current_index
                ] = translated_path

                self.sidebar.pages[
                    current_index
                ] = translated_path

                self.viewer.show_page(
                    current_index
                )

                self.right_panel.set_page(
                    translated_path
                )

        except Exception as error:

            self.right_panel.progress.setValue(
                0
            )

            self.right_panel.status.setText(
                "❌ OCR process error"
            )

            self.status_bar.setText(
                "🔴 OCR process error"
            )

            print()
            print(
                "=" * 70
            )
            print(
                "SUBPROCESS ERROR"
            )
            print(
                repr(error)
            )
            print(
                "=" * 70
            )