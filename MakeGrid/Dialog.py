import pathlib

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QDialog


class Dialog(QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)

        # Define default values
        self.matrix = dict([
            ("horizontal_cells", 8),
            ("vertical_cells", 32),
            ("width", 80),
            ("height", 320)
        ])

        self.grid = dict([
            ("horizontal_angle", 60),
            ("depth", 10),
            ("left_side_width", 5),
            ("right_side_width", 5),
            ("upper_side_height", 20),
            ("lower_side_height", 20),
            ("horizontal_spacer_width", 1.5),
            ("vertical_spacer_height", 1.5),
            ("supports_height", 0)
        ])

        # Load UI File
        loader = QUiLoader(self)
        self.dialog = loader.load(str(pathlib.Path(__file__).parent.absolute() / "dialog.ui"), parentWidget=None)

        # Set default values
        self.dialog.matrix_width.setValue(self.matrix["width"])
        self.dialog.matrix_height.setValue(self.matrix["height"])
        self.dialog.matrix_horizontal_cells.setValue(self.matrix["horizontal_cells"])
        self.dialog.matrix_vertical_cells.setValue(self.matrix["vertical_cells"])

        self.dialog.grid_horizontal_angle.setValue(self.grid["horizontal_angle"])
        self.dialog.grid_depth.setValue(self.grid["depth"])
        self.dialog.grid_left_side_width.setValue(self.grid["left_side_width"])
        self.dialog.grid_right_side_width.setValue(self.grid["right_side_width"])
        self.dialog.grid_upper_side_height.setValue(self.grid["upper_side_height"])
        self.dialog.grid_lower_side_height.setValue(self.grid["lower_side_height"])
        self.dialog.grid_horizontal_spacer_width.setValue(self.grid["horizontal_spacer_width"])
        self.dialog.grid_vertical_spacer_height.setValue(self.grid["vertical_spacer_height"])

        self.dialog.grid_supports_height.setValue(self.grid["supports_height"])

        self.dialog.buttonBox.accepted.connect(self.accept)
        self.dialog.buttonBox.rejected.connect(self.reject)

    def accept(self):
        # Collect user values
        self.matrix = dict([
            ("horizontal_cells", self.dialog.matrix_horizontal_cells.value()),
            ("vertical_cells", self.dialog.matrix_vertical_cells.value()),
            ("width", self.dialog.matrix_width.value()),
            ("height", self.dialog.matrix_height.value())
        ])

        self.grid = dict([
            ("horizontal_angle", self.dialog.grid_horizontal_angle.value()),
            ("depth", self.dialog.grid_depth.value()),
            ("left_side_width", self.dialog.grid_left_side_width.value()),
            ("right_side_width", self.dialog.grid_right_side_width.value()),
            ("upper_side_height", self.dialog.grid_upper_side_height.value()),
            ("lower_side_height", self.dialog.grid_lower_side_height.value()),
            ("horizontal_spacer_width", self.dialog.grid_horizontal_spacer_width.value()),
            ("vertical_spacer_height", self.dialog.grid_vertical_spacer_height.value()),
            ("supports_height", self.dialog.grid_supports_height.value())
        ])

        self.setResult(QDialog.Accepted)

    def reject(self):
        self.setResult(QDialog.Rejected)
