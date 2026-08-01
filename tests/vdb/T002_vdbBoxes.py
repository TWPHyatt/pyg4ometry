import os as _os
import numpy as _np
import pathlib as _pl
import pyg4ometry.gdml as _gd
import pyg4ometry.geant4 as _g4
import pyg4ometry.visualisation as _vi
import pyg4ometry.vdb as _vdb
import openvdb
import nanovdb

"""
geometry: multiple boxes
world box: (50, 50, 50) mm
box 1: (20, 20, 20) mm, inside world : translation (10, 10, 10) & (0, 0, -pi/8) rotation
box 2: (5, 5, 5) mm, inside box 1 : translation (-5, -5, -5) & (0, pi/4, 0) rotation
box 3: (20, 20, 20) mm, inside world : translation (-12.5, 0, 0) & (0 , 0, 0) rotation
"""


def Test(
    voxelSize=0.1,
    halfWidth=3.0,
    fileName="boxes",
    vis=True,
    writeGDML=True,
    writeVDB=True,
    writeNanoVDB=True,
    outputPath=None,
    testdata=None,
):

    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    # registry to store gdml data
    reg = _g4.Registry()

    # world solid
    wx = _gd.Constant("wx", "50", reg, True)
    wy = _gd.Constant("wy", "50", reg, True)
    wz = _gd.Constant("wz", "50", reg, True)
    s_w = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")

    # two box solids
    bx = _gd.Constant("bx", "20", reg, True)
    by = _gd.Constant("by", "20", reg, True)
    bz = _gd.Constant("bz", "20", reg, True)
    s_box1 = _g4.solid.Box("s_box1", bx, by, bz, reg)
    s_box2 = _g4.solid.Box("s_box2", bx / 4, by / 4, bz / 4, reg)

    # material
    m_w = _g4.nist_material_2geant4Material("G4_Galactic", reg)
    m_box1 = _g4.MaterialPredefined("G4_Fe", reg)
    m_box2 = _g4.MaterialPredefined("G4_Cu", reg)
    m_box3 = _g4.MaterialPredefined("G4_Ti", reg)

    # structure
    l_w = _g4.LogicalVolume(s_w, "G4_Galactic", "wl", reg)
    l_box1 = _g4.LogicalVolume(s_box1, m_box1, "l_box1", reg)
    l_box2 = _g4.LogicalVolume(s_box2, m_box2, "l_box2", reg)
    l_box3 = _g4.LogicalVolume(s_box1, m_box3, "l_box3", reg)
    p_box1 = _g4.PhysicalVolume([0, 0, -_np.pi / 8], [10, 10, 10], l_box1, "p_box1", l_w, reg)
    p_box2 = _g4.PhysicalVolume([0, _np.pi / 4, 0], [-5, -5, -5], l_box2, "p_box2", l_box1, reg)
    p_box3 = _g4.PhysicalVolume([0, 0, 0], [-12.5, 0, 0], l_box3, "p_box3", l_w, reg)

    # set world
    reg.setWorld(l_w.name)

    # bounding box extents (for visualisation axes)
    extentBB = l_w.extent(includeBoundingSolid=True)
    extent = l_w.extent(includeBoundingSolid=False)

    if writeGDML:
        w = _gd.Writer()
        w.addDetector(reg)
        w.write(outputPath / (fileName + ".gdml"))
        print(f"[GDML] written: {fileName}.gdml")

    if writeVDB or writeNanoVDB:
        geomvdb = _vdb.geometryVDB()  # create geometry object that inherits from ViewerBase
        geomvdb.addLogicalVolume(reg.getWorldVolume())  # add world volume to geometry object
        grids = geomvdb.buildVDBGrids(voxelSize=voxelSize, halfWidth=halfWidth)

        if writeVDB:
            openvdb.write(str(outputPath / (fileName + ".vdb")), grids=grids)
            print(f"[OpenVDB] written: {fileName}.vdb")

        if writeNanoVDB:
            # convert each OpenVDB grid to NanoVDB and write to file
            nanoGrids = [nanovdb.tools.openToNanoVDB(g) for g in grids]
            for nanoGrid in nanoGrids:
                nanovdb.io.writeGrid(str(outputPath / (fileName + ".nvdb")), nanoGrid)
            print(f"[NanoVDB] Written: {fileName}.nvdb")

    if vis:
        # visualise geometry
        v = _vi.VtkViewerNew()
        v.addLogicalVolume(l_w)
        v.addAxes(20)
        v.buildPipelinesAppend()
        v.view()
        return v
