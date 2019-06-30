import maya.OpenMaya as om
from math import fmod


class Raycast(object):
    """Methods that cast rays and check for intersections with the mesh.

    Raycasting can be very helpful for snapping to the surface, seeing if a point is inside a mesh (odd hits)
    or outside a mesh (even hits). Most methods use main function of raycast in one form or another.

    """

    def point_inside_mesh(self, point):
        hit, data = self.raycast(point, [0, 1, 0])
        return int(fmod(len(data['hit_faces']), 2))

    def point_outside_mesh(self, point):
        return not self.point_inside_mesh(point)

    def raycast_hit(self, origin, direction):
        hit, data = self.raycast(origin, direction)
        return hit

    def raycast_position(self, point):
        hit, data = self.raycast(point, [0, 1, 0])
        return [data['hit_starting_position'][0].x,
                data['hit_starting_position'][0].y,
                data['hit_starting_position'][0].z]

    def raycast(self, origin, direction):
        """Casts a ray into the scene from point in direction vector and collides with mesh.

        Args:
            origin (list): Point of origin
            direction (list):  Vector Direction

        Returns:
            hit (bool): Did the ray intersect the mesh
            data (dict): All the data recorded from the hit
        """

        mesh_list = om.MSelectionList()
        mesh_list.add(self.name())

        item = om.MDagPath()
        mesh_list.getDagPath(0, item)
        item.extendToShape()

        fn_mesh = om.MFnMesh(item)

        data = dict()
        data['ray_source'] = om.MFloatPoint(origin[0], origin[1], origin[2], 1.0)
        data['ray_direction'] = om.MFloatVector(direction[0], direction[1], direction[2])
        data['face_ids'] = None
        data['tri_ids'] = None
        data['ids_sorted'] = False
        data['test_both_vectors'] = False
        data['world_space'] = om.MSpace.kWorld
        data['max_param'] = 999999
        data['accel_params'] = None
        data['sort_hits'] = True
        data['hit_starting_position'] = om.MFloatPointArray()
        data['hit_ray_params'] = om.MFloatArray()
        data['hit_faces'] = om.MIntArray()
        data['hit_tris'] = None
        data['hit_barys_1'] = None
        data['hit_barys_2'] = None
        data['tolerance'] = 0.0001

        hit = fn_mesh.allIntersections(
            data['ray_source'],
            data['ray_direction'],
            data['face_ids'],
            data['tri_ids'],
            data['ids_sorted'],
            data['world_space'],
            data['max_param'],
            data['test_both_vectors'],
            data['accel_params'],
            data['sort_hits'],
            data['hit_starting_position'],
            data['hit_ray_params'],
            data['hit_faces'],
            data['hit_tris'],
            data['hit_barys_1'],
            data['hit_barys_2'],
            data['tolerance']
        )

        return hit, data
