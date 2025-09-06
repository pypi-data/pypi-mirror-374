from . import Project
from . import ComObjectWrapper
import numpy as np

class AsymptoticSolver(ComObjectWrapper):
    SOLVER_TYPE_SBR = 'SBR'
    SOLVER_TYPE_SBR_RAYTUBES = 'SBR_RAYTUBES'

    SOLVER_MODE_MONOSTATIC_SCATTERING = 'MONOSTATIC_SCATTERING'
    SOLVER_MODE_BISTATIC_SCATTERING = 'BISTATIC_SCATTERING'
    SOLVER_MODE_FIELD_SOURCES = 'FIELD_SOURCES'
    SOLVER_MODE_RANGE_PROFILES = 'RANGE_PROFILES'

    ACCURACY_LOW = 'LOW'
    ACCURACY_MEDIUM = 'MEDIUM'
    ACCURACY_HIGH = 'HIGH'
    ACCURACY_CUSTOM = 'CUSTOM'

    RANGE_PROFILES_WINDOW_RECTANGULAR = 'RECTANGULAR'
    RANGE_PROFILES_WINDOW_HANNING = 'HANNING'
    RANGE_PROFILES_WINDOW_HAMMING = 'HAMMING'
    RANGE_PROFILES_WINDOW_BLACKMAN = 'BLACKMAN'

    RANGE_PROFILES_MODE_RANGE_EXTEND = 'RANGE_EXTEND'
    RANGE_PROFILES_MODE_BANDWIDTH = 'BANDWIDTH'

    ANGLE_SWEEP_POINT = 'POINT'
    ANGLE_SWEEP_THETA = 'THETA'
    ANGLE_SWEEP_PHI = 'PHI'
    ANGLE_SWEEP_BOTH = 'BOTH'

    def __init__(self, project: Project) -> None:
        self.project = project
        self.com_object = project.com_object.AsymptoticSolver

    def invoke_method(self, name, *args, **kwargs):
        self.project.ensure_active()
        return super().invoke_method(name, *args, **kwargs)

    def set_solver_type(self, solver_type: str):
        self.invoke_method('SetSolverType', solver_type)

    def set_solver_mode(self, solver_mode: str):
        self.invoke_method('SetSolverMode', solver_mode)

    def set_accuracy_level(self, accuracy_level: str):
        self.invoke_method('SetAccuracyLevel', accuracy_level)

    def set_solver_store_results_as_tables_only(self, flag: bool = True):
        self.invoke_method('SetSolverStoreResultsAsTablesOnly', flag)

    def set_calculate_rcs_map_for_1d_sweeps(self, flag: bool = True):
        self.invoke_method('CalculateRCSMapFor1DSweeps', flag)

    def set_calculate_monitors(self, flag: bool = True):
        self.invoke_method('Set', 'CalculateMonitors', flag)

    def reset_polarizations(self):
        self.invoke_method('ResetPolarizations')

    def add_horizontal_polarization(self, value: float):
        self.invoke_method('AddHorizontalPolarization', value)

    def add_vertical_polarization(self, value: float):
        self.invoke_method('AddVerticalPolarization', value)

    def add_lhc_polarization(self, value: float):
        self.invoke_method('AddLHCPolarization', value)

    def add_rhc_polarization(self, value: float):
        self.invoke_method('AddRHCPolarization', value)

    def add_custom_polarization(self, theta: complex, phi: complex):
        self.invoke_method('AddCustomPolarization', theta.real, theta.imag, phi.real, phi.imag)

    def set_solver_max_number_of_reflections(self, number: int):
        self.invoke_method('SetSolverMaximumNumberOfReflections', number)

    def set_solver_range_profiles_center_frequency(self, freq: float):
        self.invoke_method('SetSolverRangeProfilesCenterFrequency', freq)

    def set_solver_range_profiles_automatic(self, flag: bool = True):
        self.invoke_method('SetSolverRangeProfilesAutomatic', flag)

    def set_solver_range_profiles_number_of_samples(self, number: int):
        self.invoke_method('SetSolverRangeProfilesNumberOfSamples', number)

    def set_solver_range_profiles_window_function(self, window: str):
        self.invoke_method('SetSolverRangeProfilesWindowFunction', window)

    def set_solver_range_profiles_spec_mode(self, mode: str):
        self.invoke_method('SetSolverRangeProfilesSpecMode', mode)

    def set_solver_range_profiles_range_extend(self, ext: float):
        self.invoke_method('SetSolverRangeProfilesRangeExtend', ext)

    def set_solver_range_profiles_bandwidth(self, bw: float):
        self.invoke_method('SetSolverRangeProfilesBandwidth', bw)

    def reset_frequency_list(self):
        self.invoke_method('ResetFrequencyList')

    def add_frequency_sweep(self, f_min: float, f_max: float, f_step: float):
        self.invoke_method('AddFrequencySweep', f_min, f_max, f_step)

    def reset_excitation_angle_list(self):
        self.invoke_method('ResetExcitationAngleList')

    def add_excitation_angle_sweep_deg(
            self, angle_sweep_type: str, theta_min: float, theta_max: float, theta_step: float,
            phi_min: float, phi_max: float, phi_step: float):
        self.invoke_method(
            'AddExcitationAngleSweep', angle_sweep_type, theta_min, theta_max, theta_step,
            phi_min, phi_max, phi_step)

    def add_excitation_angle_sweep_rad(
            self, angle_sweep_type: str, theta_min: float, theta_max: float, theta_step: float,
            phi_min: float, phi_max: float, phi_step: float):
        self.add_excitation_angle_sweep_deg(
            angle_sweep_type,
            np.rad2deg(theta_min), np.rad2deg(theta_max), np.rad2deg(theta_step),
            np.rad2deg(phi_min), np.rad2deg(phi_max), np.rad2deg(phi_step))

    def add_excitation_angle_sweep_with_rays_deg(
            self, angle_sweep_type: str, theta_min: float, theta_max: float, theta_step: float,
            phi_min: float, phi_max: float, phi_step: float):
        self.invoke_method(
            'AddExcitationAngleSweepWithRays', angle_sweep_type,
            theta_min, theta_max, theta_step, phi_min, phi_max, phi_step)

    def add_excitation_angle_sweep_with_rays_rad(
            self, angle_sweep_type: str, theta_min: float, theta_max: float, theta_step: float,
            phi_min: float, phi_max: float, phi_step: float):
        self.add_excitation_angle_sweep_with_rays_deg(
            angle_sweep_type,
            np.rad2deg(theta_min), np.rad2deg(theta_max), np.rad2deg(theta_step),
            np.rad2deg(phi_min), np.rad2deg(phi_max), np.rad2deg(phi_step))

    def reset_field_sources(self):
        self.invoke_method('ResetFieldSources')

    def set_field_source_active(self, field_source_name: str, flag: bool = True):
        self.invoke_method('SetFieldSourceActive', field_source_name, flag)

    def set_field_source_phasor(self, field_source_name: str, amplitude: float, phase: float):
        self.invoke_method('SetFieldSourcePhasor', field_source_name, amplitude, phase)

    def set_field_source_store_rays(self, field_source_name: str, flag: bool = True):
        self.invoke_method('SetFieldSourceRays', field_source_name, flag)

    def set_simultaneous_field_source_excitation(self, flag: bool = True):
        self.invoke_method('SimultaneousFieldSourceExcitation', flag)

    def set_calculate_s_params(self, flag: bool = True):
        self.invoke_method('Set', 'CalculateSParameters', flag)

    def reset_observation_angle_list(self):
        self.invoke_method('ResetObservationAngleList')

    def set_(self, flag: bool = True):
        self.invoke_method('', flag)