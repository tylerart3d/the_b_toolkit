import maya.cmds as cmds
outside = []
for uv in cmds.ls(sl=1, fl=1):
    pos = cmds.polyEditUV(uv, q=1)
    if pos[0] >=1 or pos[0] <= 0 or pos[1] >= 1 or pos[1] <=0:
        outside.append(uv)

cmds.select(outside)
