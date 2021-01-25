import pathlib

from PySide2.QtCore import QObject
from PySide2.QtUiTools import QUiLoader


class Progress(QObject):
    def __init__(self, parent=None):
        super(Progress, self).__init__(parent)

        loader = QUiLoader(self)
        self.dialog = loader.load(str(pathlib.Path(__file__).parent.absolute() / "progress.ui"), parentWidget=None)
