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
geometry: single orb
world box: (50, 50, 50) mm
orb 1: (20) mm, inside world : translation (0, 0, 0) & (0, 0, 0) rotation
"""


def Test(
    voxelSize=0.1,
    halfWidth=3.0,
    fileName="orb",
    vis=True,
    n_slice=16,
    n_stack=16,
    writeGDML=True,
    writeVDB=True,
    writeNanoVDB=True,
    outputPath=None,
    testdata=None,
):

    fileName = fileName + "Geometry"

    if not outputPath:
        outputPath = _pl.Path(__file__).parent

    # registry to store gdml data
    reg = _g4.Registry()

    # world solid
    wx = _gd.Constant("wx", "50", reg, True)
    wy = _gd.Constant("wy", "50", reg, True)
    wz = _gd.Constant("wz", "50", reg, True)
    s_w = _g4.solid.Box("ws", wx, wy, wz, reg, "mm")

    # orb solid
    ormax = _gd.Constant("rmax", "20", reg, True)
    s_orb1 = _g4.solid.Orb("s_orb1", ormax, reg, "mm", nslice=n_slice, nstack=n_stack)

    # material
    m_w = _g4.nist_material_2geant4Material("G4_Galactic", reg)
    m_orb1 = _g4.MaterialPredefined("G4_Pb", reg)

    # structure
    l_w = _g4.LogicalVolume(s_w, m_w, "l_world", reg, "mm")
    l_orb1 = _g4.LogicalVolume(s_orb1, m_orb1, "l_orb1", reg, "mm")
    p_orb1 = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], l_orb1, "p_orb1", l_w, reg)

    # set world
    reg.setWorld(l_w.name)

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

    # bounding box extents (for visualisation axes)
    extentBB = l_w.extent(includeBoundingSolid=True)
    extent = l_w.extent(includeBoundingSolid=False)

    if vis:
        # visualise geometry
        v = _vi.VtkViewerNew()
        v.addLogicalVolume(l_w)
        v.addAxes(20)
        v.buildPipelinesAppend()
        v.view()
        return v
