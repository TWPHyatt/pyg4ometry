import pyg4ometry

import T001_vdbBox
import T002_vdbMultipleBoxes


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


def test_vdbMultipleBoxes(tmptestdir, testdata):
    T002_vdbMultipleBoxes.Test(
        voxelSize=0.1,
        halfWidth=3.0,
        fileName="multipleboxes",
        vis=False,
        writeGDML=True,
        writeVDB=True,
        writeNanoVDB=True,
        outputPath=tmptestdir,
        testdata=testdata,
    )
