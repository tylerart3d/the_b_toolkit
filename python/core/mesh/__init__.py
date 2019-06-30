import pymel.core as pm

import spherize
import raycast
import attach_to_mesh


class MeshBase(spherize.Spherize,
               raycast.Raycast,
               attach_to_mesh.AttachToMesh):
    pass


class TMesh(pm.nt.Mesh, MeshBase):
    node_type = "t_mesh"
    attr_name = 't_node'

    @classmethod
    def _isVirtual(cls, obj, name):
        fn = pm.api.MFnDependencyNode(obj)
        try:
            if fn.hasAttribute(cls.attr_name):
                plug = fn.findPlug(cls.attr_name)
                if plug.asString() == cls.node_type:
                    return True
                return False
        except:
            pass
        return False

    @classmethod
    def _createVirtual(cls, **kwargs):
        pass

    @classmethod
    def _preCreateVirtual(cls, **kwargs):
        """This is called before creation. python allowed."""
        return kwargs

    @classmethod
    def _postCreateVirtual(cls, newNode):
        pass
