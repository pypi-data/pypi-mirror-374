from . import Project
from . import Shape

class Cylinder(Shape):
    AXIS_X = 'x'
    AXIS_Y = 'y'
    AXIS_Z = 'z'

    def __init__(self, project: Project) -> None:
        super().__init__(project, project.com_object.Cylinder)

    def set_axis(self, axis: str):
        self.invoke_method('Axis', axis)

    def set_outer_radius(self, radius: float):
        self.invoke_method('Outerradius', radius)

    def set_inner_radius(self, radius: float):
        self.invoke_method('Innerradius', radius)

    def set_x_center(self, center: float):
        self.invoke_method('Xcenter', center)

    def set_y_center(self, center: float):
        self.invoke_method('Ycenter', center)

    def set_z_center(self, center: float):
        self.invoke_method('Zcenter', center)

    def set_x_range(self, x_min: float, x_max: float):
        self.invoke_method('Xrange', x_min, x_max)

    def set_y_range(self, y_min: float, y_max: float):
        self.invoke_method('Yrange', y_min, y_max)

    def set_z_range(self, z_min: float, z_max: float):
        self.invoke_method('Zrange', z_min, z_max)

    def set_num_segments(self, num_segments: int):
        self.invoke_method('Segments', num_segments)

    def set_smooth_geometry(self):
        self.set_num_segments(0)