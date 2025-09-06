from . import Project
from . import ComObjectWrapper

class MeshShapes(ComObjectWrapper):
    def __init__(self, project: Project) -> None:
        self.project = project
        self.com_object = project.com_object.MeshShapes

    def invoke_method(self, name, *args, **kwargs):
        self.project.ensure_active()
        return super().invoke_method(name, *args, **kwargs)

    def reset(self):
        self.invoke_method('Reset')

    def delete(self, mesh_shape_name: str):
        self.invoke_method('Delete', mesh_shape_name)

    def rename(self, old_mesh_shape_name: str, new_mesh_shape_name: str):
        self.invoke_method('Rename', old_mesh_shape_name, new_mesh_shape_name)

    def create_folder(self, name: str):
        self.invoke_method('NewFolder', name)

    def delete_folder(self, name: str):
        self.invoke_method('DeleteFolder', name)

    def rename_folder(self, old_name: str, new_name: str):
        self.invoke_method('RenameFolder', old_name, new_name)

    def change_material(self, mesh_shape_name: str, material_name: str):
        self.invoke_method('ChangeMaterial', mesh_shape_name, material_name)

    def add_name(self, element_name: str):
        self.invoke_method('AddName', element_name)

    def delete_multiple(self):
        self.invoke_method('DeleteMultiple')

    def set_tolerance(self, value: float):
        self.invoke_method('Tolerance', value)

    def resolve_intersections(self):
        self.invoke_method('ResolveIntersections')

    def set_mesh_element_size(self, value: float):
        self.invoke_method('MeshElementSize', value)

    def create_mesh_shapes_by_facetting(self):
        self.invoke_method('CreateMeshShapesByFacetting')

    def create_mesh_shapes_by_remeshing(self):
        self.invoke_method('CreateMeshShapesByRemeshing')