import math
import FreeCAD
import FreeCADGui
import Part


class GridRenderer:
    def __init__(self, matrix, grid):

        self.cylinder = None
        self.punch_tool = None

        try:
            self._parse_matrix(matrix)
            self._parse_grid(grid)
            self._prepare()

        except Exception as inst:
            FreeCAD.Console.PrintError(inst)

    def _parse_matrix(self, matrix):
        matrix_horizontal_cells = int(matrix["horizontal_cells"])
        matrix_vertical_cells = int(matrix["vertical_cells"])
        matrix_width = float(matrix["width"])
        matrix_height = float(matrix["height"])

        if matrix_horizontal_cells < 1:
            raise Exception("matrix[\"horizontal_cells\"] must be: >1")
        if matrix_vertical_cells < 1:
            raise Exception("matrix[\"vertical_cells\"] must be: >1")
        if matrix_width < 1:
            raise Exception("matrix[\"width\"] must be: >1")
        if matrix_height < 1:
            raise Exception("matrix[\"height\"] must be: >1")

        self.matrix_horizontal_cells = matrix_horizontal_cells
        self.matrix_vertical_cells = matrix_vertical_cells
        self.matrix_width = matrix_width
        self.matrix_height = matrix_height

        FreeCAD.Console.PrintMessage("Matrix size : {0}x{1} cells / {2}x{3} mm\n"
                                     .format(self.matrix_horizontal_cells,
                                             self.matrix_vertical_cells,
                                             self.matrix_width,
                                             self.matrix_height))
        FreeCADGui.updateGui()

    def _parse_grid(self, grid):
        grid_horizontal_angle = float(grid["horizontal_angle"])
        grid_depth = float(grid["depth"])
        grid_left_side_width = float(grid["left_side_width"])
        grid_right_side_width = float(grid["right_side_width"])
        grid_upper_side_height = float(grid["upper_side_height"])
        grid_lower_side_height = float(grid["lower_side_height"])
        grid_horizontal_spacer_width = float(grid["horizontal_spacer_width"])
        grid_vertical_spacer_height = float(grid["vertical_spacer_height"])
        grid_supports_height = float(grid["supports_height"])

        self.grid_horizontal_angle = grid_horizontal_angle
        self.grid_depth = grid_depth
        self.grid_left_side_width = grid_left_side_width
        self.grid_right_side_width = grid_right_side_width
        self.grid_upper_side_height = grid_upper_side_height
        self.grid_lower_side_height = grid_lower_side_height
        self.grid_horizontal_spacer_width = grid_horizontal_spacer_width
        self.grid_vertical_spacer_height = grid_vertical_spacer_height
        self.grid_supports_height = grid_supports_height

        FreeCAD.Console.PrintMessage("""Grid dimensions :
                                    - angle : {0}°
                                    - depth : {1} mm
                                    - sides horizontal : L={2} mm R={3} mm
                                    - sides vertical : T={4} mm B={5} mm
                                    - spacers (H/V) : {6}/{7} mm
                                    - supports thickness : {8} mm\n"""
                                     .format(self.grid_horizontal_angle,
                                             self.grid_depth,
                                             self.grid_left_side_width,
                                             self.grid_right_side_width,
                                             self.grid_upper_side_height,
                                             self.grid_lower_side_height,
                                             self.grid_horizontal_spacer_width,
                                             self.grid_vertical_spacer_height,
                                             self.grid_supports_height))
        FreeCADGui.updateGui()

    def _prepare(self):
        self._punch_depth_offset = 1
        self.led_vertical_height = self.matrix_height / self.matrix_vertical_cells - self.grid_vertical_spacer_height
        self.grid_horizontal_inner_circumference = self.matrix_width
        self.cylinder_inner_height = self.matrix_height + self.grid_upper_side_height + self.grid_lower_side_height \
                                     - self.grid_supports_height * 2
        self.cylinder_inner_diameter = (self.grid_horizontal_inner_circumference + self.grid_left_side_width * 2) \
                                       * (360 / math.pi) / self.grid_horizontal_angle
        self.cylinder_inner_radius = self.cylinder_inner_diameter / 2
        self.cylinder_outer_diameter = self.cylinder_inner_diameter + self.grid_depth * 2
        self.cylinder_outer_radius = self.cylinder_outer_diameter / 2
        self.cylinder_outer_height = self.matrix_height + self.grid_upper_side_height + self.grid_lower_side_height
        self.cylinder_outer_circumference = ((math.pi * self.cylinder_outer_diameter) / 360) \
                                            * self.grid_horizontal_angle

        self.led_horizontal_width = (self.cylinder_outer_circumference
                                     - self.grid_left_side_width
                                     - self.grid_right_side_width
                                     - self.grid_horizontal_spacer_width * self.matrix_horizontal_cells) \
                                    / self.matrix_horizontal_cells

        self.led_horizontal_angle = math.degrees(self.led_horizontal_width / self.cylinder_outer_radius)
        self.led_horizontal_bisector_angle = self.led_horizontal_angle / 2

        self.spacer_horizontal_angle = math.degrees(self.grid_horizontal_spacer_width / self.cylinder_outer_radius)
        self.spacer_horizontal_bisector_angle = self.spacer_horizontal_angle / 2

        self.side_left_angle = math.degrees(self.grid_left_side_width / self.cylinder_outer_radius)
        # self.side_right_angle = math.degrees(self.grid_right_side_outer_circumference/self.cylinder_outer_radius)

    def render(self):

        FreeCAD.Console.PrintMessage("Please be patient while the grid is being created :\n")
        FreeCADGui.updateGui()

        try:
            self._create_cylinder()
            self._create_punch_tool()
            self._punch_holes()
            self._clean_the_workshop()

        except Exception as inst:
            FreeCAD.Console.PrintError(inst)

    def _create_cylinder(self):
        FreeCAD.Console.PrintMessage("- Creating cylinder ... ")
        FreeCADGui.updateGui()

        inner_cylinder = Part.makeCylinder(self.cylinder_inner_radius, self.cylinder_inner_height,
                                           FreeCAD.Vector(0, 0, self.grid_supports_height), FreeCAD.Vector(0, 0, 1),
                                           self.grid_horizontal_angle)
        outer_cylinder = Part.makeCylinder(self.cylinder_outer_radius, self.cylinder_outer_height,
                                           FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), self.grid_horizontal_angle)
        self.cylinder = outer_cylinder.cut(inner_cylinder)
        FreeCAD.ActiveDocument.recompute()
        FreeCAD.Console.PrintMessage("OK\n")

    def _create_punch_tool(self):
        FreeCAD.Console.PrintMessage("- Creating punch tool (long operation) ... ")
        FreeCADGui.updateGui()

        box = []
        for x in range(self.matrix_horizontal_cells):
            box.append([])
            for y in range(self.matrix_vertical_cells):
                V1 = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), self.led_horizontal_bisector_angle).multVec(
                    FreeCAD.Vector(self.cylinder_inner_radius - self._punch_depth_offset, 0, 0))
                V2 = FreeCAD.Vector(self.cylinder_inner_radius - self._punch_depth_offset, 0, 0)
                V3 = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), -self.led_horizontal_bisector_angle).multVec(
                    FreeCAD.Vector(self.cylinder_inner_radius - self._punch_depth_offset, 0, 0))
                V4 = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), -self.led_horizontal_bisector_angle).multVec(
                    FreeCAD.Vector(self.cylinder_outer_radius + self._punch_depth_offset, 0, 0))
                V5 = FreeCAD.Vector(self.cylinder_outer_radius + self._punch_depth_offset, 0, 0)
                V6 = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), self.led_horizontal_bisector_angle).multVec(
                    FreeCAD.Vector(self.cylinder_outer_radius + self._punch_depth_offset, 0, 0))
                L1 = Part.LineSegment(V1, V6).toShape()
                A2 = Part.Arc(V1, V2, V3).toShape()
                L3 = Part.LineSegment(V4, V3).toShape()
                A4 = Part.Arc(V4, V5, V6).toShape()
                W = Part.Wire([L1, A2, L3, A4])
                F = Part.Face(W)
                P = F.extrude(FreeCAD.Vector(0, 0, self.led_vertical_height))
                box[x].append(FreeCAD.ActiveDocument.addObject("Part::Feature", "Hole"))
                box[x][y].Shape = P

                # Object orientation
                box[x][y].Placement.Rotation = \
                    FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1),
                                     self.side_left_angle +
                                     self.led_horizontal_bisector_angle +
                                     self.spacer_horizontal_bisector_angle +
                                     (self.led_horizontal_angle + self.spacer_horizontal_angle) * x)
                # Object translation Z
                box[x][y].Placement.Base = \
                    box[x][y].Placement.Base + \
                    FreeCAD.Vector(
                        0,
                        0,
                        self.grid_lower_side_height +
                        self.grid_vertical_spacer_height / 2 +
                        (self.led_vertical_height + self.grid_vertical_spacer_height) * y)

        shapes = None
        for x in range(self.matrix_horizontal_cells):
            for y in range(self.matrix_vertical_cells):
                if shapes is not None:
                    shapes = shapes.fuse(box[x][y].Shape)
                else:
                    shapes = box[0][0].Shape

        self.punch_tool = FreeCAD.ActiveDocument.addObject("Part::Feature", "boxes")
        self.punch_tool.Shape = shapes
        for bx in box:
            for by in bx:
                FreeCAD.ActiveDocument.removeObject(by.Name)
        FreeCAD.ActiveDocument.recompute()
        FreeCAD.Console.PrintMessage("OK\n")

    def _punch_holes(self):
        FreeCAD.Console.PrintMessage("- Punching holes ... ")
        FreeCADGui.updateGui()

        grid = self.cylinder.cut(self.punch_tool.Shape)

        Part.show(grid)
        FreeCAD.ActiveDocument.removeObject(self.punch_tool.Name)

        FreeCAD.ActiveDocument.recompute()
        FreeCAD.Console.PrintMessage("OK\n")

    def _clean_the_workshop(self):
        FreeCADGui.SendMsgToActiveView("ViewFit")
        FreeCAD.Console.PrintMessage("Operation completed!\n")
        FreeCADGui.updateGui()
