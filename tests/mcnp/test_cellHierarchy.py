import pyg4ometry
import numpy as _np


def test_twoBoxHierarchy(vis, write):
    """

    :param write:
    :return:
    """
    reg = pyg4ometry.mcnp.Registry()

    # INNER LITTLE BOX
    cLittleBox = pyg4ometry.mcnp.Cell()
    sLittleBox = pyg4ometry.mcnp.BOX(-10, -10, -10, 20, 0, 0, 0, 20, 0, 0, 0, 20, reg=reg)
    cLittleBox.addSurface(sLittleBox)
    gLittleBox = pyg4ometry.mcnp.Complement(sLittleBox)
    cLittleBox.addGeometry(gLittleBox)

    # OUTER BIG BOX
    cBigBox = pyg4ometry.mcnp.Cell(reg=reg)
    sBigBox = pyg4ometry.mcnp.BOX(-50, -50, -50, 100, 0, 0, 0, 100, 0, 0, 0, 100, reg=reg)
    cBigBox.addSurface(sBigBox)
    cBigBox.addSurface(sLittleBox)
    gBigBox = pyg4ometry.mcnp.Complement(sBigBox)
    cBigBox.addGeometry(gBigBox)

    # TRANSFORM LITTLE BOX CELL
    angle = 45
    rotationMatrixZ = [
        [_np.cos(_np.radians(angle)), -_np.sin(_np.radians(angle)), 0],
        [_np.sin(_np.radians(angle)), _np.cos(_np.radians(angle)), 0],
        [0, 0, 1],
    ]
    cLittleBox_p = cLittleBox.transformCell(rotation=rotationMatrixZ, translation=[25, 0, 0])
    # cLittleBox_p = cLittleBox_p.transformCell(translation=[-25, 0, 0])

    # LITTLE BOX INSIDE BIG BOX
    cBigBox.addChildCell(
        cLittleBox_p
    )  # will always add childCell surfaces to reg if parent cell has a reg

    # VOID OUTSIDE
    cVoid = pyg4ometry.mcnp.Cell(reg=reg)
    cVoid.addSurface(sBigBox)
    cVoid.addGeometry(sBigBox)

    # MATERIALS
    m0 = pyg4ometry.mcnp.Material(0, reg=reg)
    m1 = pyg4ometry.mcnp.Material(1, -0.001225, reg=reg)
    m2 = pyg4ometry.mcnp.Material(2, -0.92, reg=reg)

    cVoid.addMaterial(m0)
    cBigBox.addMaterial(m1)
    cLittleBox.addMaterial(m2)

    # IMPORTANCE
    p = f"p"
    i0 = pyg4ometry.mcnp.IMP(p, 0)
    i1 = pyg4ometry.mcnp.IMP(p, 1)

    cVoid.addImportance(i0)
    cBigBox.addImportance(i1)
    cLittleBox.addImportance(i1)

    if write:
        f = pyg4ometry.mcnp.Writer(columnMax=75)
        title = f"CELL INSIDE CELL"
        f.setTitle(title)
        f.addGeometry(reg=reg)
        fileName = f"i-twoBoxHierarchy-Test0.txt"
        f.write(fileName)

    if vis:
        v = pyg4ometry.visualisation.VtkViewer()
        v.addAxes()
        # add mesh(es) simple to VTK viewer
        v.view()


# remove comment when debugging
test_twoBoxHierarchy(write=True, vis=False)

if __name__ == "__main__":
    test_twoBoxHierarchy(write=True, vis=False)
