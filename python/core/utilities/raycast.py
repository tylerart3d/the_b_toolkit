"""Simple utility that casts rays

Casts intersection rays from the origin in the direction of the vector colliding with the mesh shape.
Can be used to find if inside an enclosed mesh or outside by counting odd / even collisions.

"""

import maya.OpenMaya as om
from math import fmod


def raycast(mesh, origin, direction, return_type='position'):
    """Casts a ray into the scene from point in direction vector and collides with mesh.

    Args:
        mesh (str): Name of mesh shape
        origin (list): Point of origin
        direction (list):  Vector Direction
        return_type (str):

    Returns:
        value (variable): depends on return_type
    """

    mesh_list = om.MSelectionList()
    mesh_list.add(mesh)

    item = om.MDagPath()
    mesh_list.getDagPath(0, item)
    item.extendToShape()

    fn_mesh = om.MFnMesh(item)

    ray_source = om.MFloatPoint(origin[0], origin[1], origin[2], 1.0)
    ray_direction = om.MFloatVector(direction[0], direction[1], direction[2])
    face_ids = None
    tri_ids = None
    ids_sorted = False
    test_both_vectors = False
    world_space = om.MSpace.kWorld
    max_param = 999999
    accel_params = None
    sort_hits = True
    hit_starting_position = om.MFloatPointArray()
    hit_ray_params = om.MFloatArray()
    hit_faces = om.MIntArray()
    hit_tris = None
    hit_barys_1 = None
    hit_barys_2 = None
    tolerance = 0.0001

    hit = fn_mesh.allIntersections(
        ray_source,
        ray_direction,
        face_ids,
        tri_ids,
        ids_sorted,
        world_space,
        max_param,
        test_both_vectors,
        accel_params,
        sort_hits,
        hit_starting_position,
        hit_ray_params,
        hit_faces,
        hit_tris,
        hit_barys_1,
        hit_barys_2,
        tolerance
    )

    # Return first hit position
    if return_type == 'position':
        return [hit_starting_position[0].x, hit_starting_position[0].y, hit_starting_position[0].z]

    # Return Hit Faces
    elif return_type == 'faces':
        return hit_faces

    # Return True if Inside Mesh
    elif return_type == 'inside':
        return int(fmod(len(hit_faces), 2))

    elif return_type == 'outside':
        return not int(fmod(len(hit_faces), 2))

    else:
        return hit
