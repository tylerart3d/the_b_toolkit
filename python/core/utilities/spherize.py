"""Simple utility that spherizes mesh

"""
import pymel.core as pm
import math
import logging


def main(radius=10):
    selection = pm.ls(sl=1, fl=1)
    if not selection:
        logging.error('Select object to spherize')

    meshes = []
    for node in selection:
        if type(node) == pm.nt.Transform:
            meshes += [mesh for mesh in pm.listRelatives(node, ad=1) if type(mesh) == pm.nt.Mesh]
        elif type(node) == pm.nt.Mesh:
            meshes.append(node)

    for mesh in meshes:
        offset = pm.xform(mesh.getParent(), q=1, rp=1, ws=1)
        for i in range(pm.polyEvaluate(mesh, v=1)):
            pos = pm.xform('{0}.vtx[{1}]'.format(mesh.name(), i), q=1, ws=1, t=1)
            pos = [pos[0] - offset[0], pos[1] - offset[1], pos[2] - offset[2]]
            mult = radius / math.sqrt(sum(j ** 2 for j in pos))
            new_pos = [pos[0] * mult, pos[1] * mult, pos[2] * mult]
            new_pos = [new_pos[0] + offset[0], new_pos[1] + offset[1], new_pos[2] + offset[2]]
            pm.xform('{0}.vtx[{1}]'.format(mesh.name(), i), ws=1, t=new_pos)


if __name__ == '__main__':
    main()
