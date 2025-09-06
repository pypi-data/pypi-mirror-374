from ..CST.project import Project
from ..CST import FarfieldPlot
from .. import FFS
from .farfields import Farfield
import numpy as np
import pathlib
import os.path

class ASCIIFarfieldExporter:
    DEFAULT_STEP_DEG: float = 5.0

    def __init__(self) -> None:
        self.coord_system = FarfieldPlot.COORD_SYSTEM_SPHERICAL
        self.plot_mode = FarfieldPlot.PLOT_MODE_EFIELD
        self.polar_angle_step = ASCIIFarfieldExporter.DEFAULT_STEP_DEG
        self.lateral_angle_step = ASCIIFarfieldExporter.DEFAULT_STEP_DEG
        self.current_farfield: Farfield = None
        self.ascii_version = FarfieldPlot.ASCII_VERSION_2010
        self.origin = (0.0, 0.0, 0.0)
        self.radius = 1.0
        self.current_ffs: FFS.Farfield = None

    def set_coord_system(self, coord_system: str):
        self.coord_system = coord_system

    def set_plot_mode(self, plot_mode: str):
        self.plot_mode = plot_mode

    def set_polar_angle_step_deg(self, step_deg: float):
        self.polar_angle_step = step_deg

    def set_polar_angle_step_rad(self, step_rad: float):
        self.set_polar_angle_step_deg(np.rad2deg(step_rad))

    def set_lateral_angle_step_deg(self, step_deg: float):
        self.lateral_angle_step = step_deg

    def set_lateral_angle_step_rad(self, step_rad: float):
        self.set_lateral_angle_step_deg(np.rad2deg(step_rad))

    def set_ascii_version(self, ascii_version: str):
        self.ascii_version = ascii_version

    def set_origin(self, x: float, y: float, z: float):
        self.origin = (x, y, z)

    def set_radius(self, radius: float):
        self.radius = radius

    def prepare(self, farfield: Farfield):
        self.current_farfield = farfield
        self.current_farfield.select()
        self.__prepare_ffplot()
        self.__export_file()

    def export_abs(self):
        return None

    def export_complex_theta(self):
        return self.current_ffs.get_theta_component()

    def export_complex_phi(self):
        return self.current_ffs.get_phi_component()

    def __prepare_ffplot(self):
        ffplot = FarfieldPlot(self.current_farfield.project)
        ffplot.reset()
        ffplot.set_plot_mode(self.plot_mode)
        ffplot.set_plot_type(FarfieldPlot.PLOT_TYPE_3D)
        ffplot.set_coord_system(self.coord_system)
        ffplot.set_db_unit(FarfieldPlot.UNIT_CODE_0) # basic units
        ffplot.set_origin(self.origin[0], self.origin[1], self.origin[2])
        ffplot.set_polarization_linear()
        ffplot.set_lock_steps(False)
        ffplot.set_theta_step_deg(self.polar_angle_step)
        ffplot.set_phi_step_deg(self.lateral_angle_step)
        ffplot.set_virtual_sphere_radius(self.radius)
        ffplot.set_scale_linear()
        ffplot.set_ascii_export_version(self.ascii_version)
        ffplot.plot()

    def __export_file(self):
        ffplot = FarfieldPlot(self.current_farfield.project)
        proj = ffplot.project
        tmp_path = proj.get_project_path(Project.PATH_TYPE_TEMP)
        file_path = os.path.join(tmp_path, 'tmp_ff.ffs')
        ffplot.export_source_as_ascii(file_path)
        self.__load_ffs(file_path)
        os.remove(file_path)

    def __load_ffs(self, path):
        parser = FFS.Parser()
        parser.parse_string(pathlib.Path(path).read_text())
        self.current_ffs = parser.get_farfields()[0]