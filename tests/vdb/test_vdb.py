import pyg4ometry

import T001_vdbBox
import T002_vdbBoxes
import T003_vdbOrb
import T004_vdbOrbs


def test_vdbBox(tmptestdir, testdata):
    T001_vdbBox.Test(
        voxelSize=0.1,
        halfWidth=3.0,
        fileName="box",
        vis=False,
        writeGDML=True,
        writeVDB=True,
        writeNanoVDB=True,
        outputPath=tmptestdir,
        testdata=testdata,
    )


def test_vdbBoxes(tmptestdir, testdata):
    T002_vdbBoxes.Test(
        voxelSize=0.1,
        halfWidth=3.0,
        fileName="boxes",
        vis=False,
        writeGDML=True,
        writeVDB=True,
        writeNanoVDB=True,
        outputPath=tmptestdir,
        testdata=testdata,
    )


def test_vdbOrb(tmptestdir, testdata):
    T003_vdbOrb.Test(
        voxelSize=0.1,
        halfWidth=3.0,
        fileName="orb",
        vis=False,
        writeGDML=True,
        writeVDB=True,
        writeNanoVDB=True,
        outputPath=tmptestdir,
        testdata=testdata,
    )


def test_vdbOrbs(tmptestdir, testdata):
    T004_vdbOrbs.Test(
        voxelSize=0.1,
        halfWidth=3.0,
        fileName="orbs",
        vis=False,
        writeGDML=True,
        writeVDB=True,
        writeNanoVDB=True,
        outputPath=tmptestdir,
        testdata=testdata,
    )
