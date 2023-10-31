import sys

from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt


def main():
    app = QApplication([])

    label = QLabel('Hello World!')
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.resize(200, 100)
    label.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
