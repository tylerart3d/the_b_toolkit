import pymel.core as pm
from core import log_tools

logger = log_tools.logger(__name__)


class AttachToMesh(object):
    def attach_to_mesh(self, transforms, group=True):
        """ Attaches other transforms to the closest surface of the mesh.

        Often used to attach fractured meshes to deforming / animating surface. Take note that this method
        loads 'nearestPointOnMesh' plugin.

        Args:
            transforms (list): List of transforms to attach to mesh
            group (bool): Group follicles
        """

        # Load plugin
        if not pm.pluginInfo('nearestPointOnMesh', q=1, l=1):
            try:
                pm.loadPlugin('nearestPointOnMesh')
            except RuntimeError:
                logger.error('Cannot load "nearestPointOnMesh" plugin. attach_to_mesh cannot be ran')
                return

        node = pm.createNode('nearestPointOnMesh')
        self.worldMesh.connect(node.inMesh)

        follicles = []
        for transform in transforms:
            bbox = transform.getBoundingBox()
            lower_bounds = pm.dt.Vector(bbox[0][0], bbox[0][1], bbox[0][2])
            upper_bounds = pm.dt.Vector(bbox[1][0], bbox[1][1], bbox[1][2])
            position = (lower_bounds + upper_bounds) * 0.5
            node.inPosition.set(position.x, position.y, position.z)
            uv = [node.parameterU.get(), node.parameterV.get()]
            follicles.append(self._create_follicle(transform, uv))

        if group:
            group = pm.group(n=('%s_Deformed' % (self.getParent().name())), em=1, w=1)
            pm.parent(follicles, group)

        pm.delete(node)
        pm.select(self.getParent(), r=1)

    def _create_follicle(self, transform, uv):
        """Internal method for attach_to_mesh to create follicles, parent, and loop over
        Args:
            transform (nt.Transform): Node to parent to follicle
            uv (list): Position of follicle in UV space

        Returns:
            follicle_dag
        """
        follicle_shape = pm.createNode('follicle')
        follicle = follicle_shape.getParent()
        self.worldMatrix[0].connect(follicle_shape.inputWorldMatrix)
        self.outMesh.connect(follicle_shape.inputMesh)
        follicle_shape.outTranslate.connect(follicle.translate)
        follicle_shape.outRotate.connect(follicle.rotate)
        follicle.translate.lock()
        follicle.rotate.lock()
        follicle_shape.parameterU.set(uv[0])
        follicle_shape.parameterV.set(uv[1])
        pm.parent(transform, follicle)
        return follicle
