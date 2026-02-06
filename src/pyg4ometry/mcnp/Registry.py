import numpy as _np
from .Transformation import TR, TRCL


class Registry:
    def __init__(self):
        self.cellDict = {}
        self.surfaceDict = {}
        self.transformationDict = {}
        self.materialDict = {}

    def addCell(self, cell, replace=False):
        if replace:
            if cell.cellNumber not in self.cellDict:
                msg = f"Could not find cell {cell.cellNumber} in registry."
                raise TypeError(msg)
            else:
                self.cellDict[cell.cellNumber] = cell
        elif not replace:
            if cell.cellNumber not in self.cellDict:
                cell.cellNumber = self.getNewCellNumber()
            self.cellDict[cell.cellNumber] = cell
        else:
            msg = "Replace can only be True or False when adding a cell to registry."
            raise TypeError(msg)

    def addSurface(self, surface, replace=False):
        if replace:
            if surface.surfaceNumber not in self.surfaceDict:
                msg = f"Could not find surface {surface.surfaceNumber} in registry."
                raise TypeError(msg)
            else:
                self.surfaceDict[surface.surfaceNumber] = surface
        elif not replace:
            if surface.surfaceNumber not in self.surfaceDict:
                surface.surfaceNumber = self.getNewSurfaceNumber()
            self.surfaceDict[surface.surfaceNumber] = surface
        else:
            msg = "Replace can only be True or False when adding a surface to registry."
            raise TypeError(msg)

    def addTransformation(self, transformation, replace=False):
        if replace:
            if transformation.transformationNumber not in self.transformationDict:
                msg = f"Could not find transformation TRCL {transformation.transformationNumber} in registry."
                raise TypeError(msg)
            else:
                self.transformationDict[transformation.transformationNumber] = transformation
        elif not replace:
            if transformation.transformationNumber not in self.transformationDict:
                transformation.transformationNumber = self.getNewTransformationNumber()
            self.transformationDict[transformation.transformationNumber] = transformation

    def addMaterial(self, material, replace=False):
        if replace:
            if material.materialNumber not in self.materialDict:
                msg = f"Could not find material {material.materialNumber} in registry."
                raise TypeError(msg)
            else:
                self.materialDict[material.materialNumber] = material
        elif not replace:
            if material.materialNumber not in self.materialDict:
                if material.materialNumber != 0:
                    material.materialNumber = self.getNewMaterialNumber()
            self.materialDict[material.materialNumber] = material
        else:
            msg = "Replace can only be True or False when adding a material to registry."
            raise TypeError(msg)

    def getNewCellNumber(self):
        if len(self.cellDict.keys()) == 0:
            return 1
        return max(self.cellDict.keys()) + 1

    def getNewSurfaceNumber(self):
        if len(self.surfaceDict.keys()) == 0:
            return 1
        return int(max(self.surfaceDict.keys())) + 1

    def getNewMaterialNumber(self):
        if len(self.materialDict.keys()) == 0:
            return 1
        return max(self.materialDict.keys()) + 1

    def getNewTransformationNumber(self):
        if len(self.transformationDict.keys()) == 0:
            return 1
        return max(self.transformationDict.keys()) + 1

    def updateRegistry(self):
        for cell in self.cellDict.values():
            if cell.material:
                if cell.material.materialNumber is None:
                    self.addMaterial(cell.material, replace=False)
                else:
                    self.addMaterial(cell.material, replace=True)
            if cell.transformation:
                if cell.transformation.transformationNumber is None:
                    self.addTransformation(cell.transformation, replace=False)
                else:
                    self.addTransformation(cell.transformation, replace=True)
            for surface in cell.surfaceList(cell.geometry):
                if surface:
                    if surface.surfaceNumber is None:
                        self.addSurface(surface, replace=False)
                    else:
                        self.addSurface(surface, replace=True)
                if surface.transformation:
                    if surface.transformation.transformationNumber is None:
                        self.addTransformation(surface.transformation, replace=False)
                    else:
                        self.addTransformation(surface.transformation, replace=True)

    def hashTransformations(self):
        # hash transformations
        toDelete = set()
        transformations = list(self.transformationDict.values())
        for i, transformation in enumerate(transformations):
            for otherTransformation in transformations[i + 1 :]:
                if (
                    _np.allclose(
                        transformation.rotationMatrix,
                        otherTransformation.rotationMatrix,
                        rtol=1e-6,
                        atol=1e-9,
                    )
                    and _np.allclose(
                        transformation.displacementVector,
                        otherTransformation.displacementVector,
                        rtol=1e-6,
                        atol=1e-9,
                    )
                    and _np.isclose(
                        transformation.displacementOrigin,
                        otherTransformation.displacementOrigin,
                        rtol=1e-6,
                        atol=1e-9,
                    )
                    and transformation.angles == otherTransformation.angles
                ):
                    tNumMax = max(
                        transformation.transformationNumber,
                        otherTransformation.transformationNumber,
                    )
                    tNumMin = min(
                        transformation.transformationNumber,
                        otherTransformation.transformationNumber,
                    )

                    # test tNumMin not for deletion
                    if tNumMin in toDelete:
                        msg = f"transformation {tNumMin} is already marked for deletion during hashing"
                        raise ValueError(msg)

                    # redirect registry references
                    for cell in self.cellDict:
                        for surface in cell.surfaceList(cell.geometry):
                            if surface.transformation.transformationNumber == tNumMax:
                                surface.transformation = self.transformationDict[tNumMin]

                    toDelete.add(tNumMax)

        # delete duplicates
        for tNum in toDelete:
            del self.transformationDict[tNum]

    def hashMaterials(self):
        # hash materials
        toDelete = set()
        materials = list(self.materialDict.values())

        for i, material in enumerate(materials):
            for otherMaterial in materials[i + 1 :]:
                if (
                    _np.isclose(material.density, otherMaterial.density, rtol=1e-6, atol=1e-9)
                    and _np.allclose(material.zk, otherMaterial.zk, rtol=1e-6, atol=1e-9)
                    and _np.allclose(material.fk, otherMaterial.fk, rtol=1e-6, atol=1e-9)
                ):
                    mNumMax = max(material.transformationNumber, otherMaterial.materialNumber)
                    mNumMin = min(material.transformationNumber, otherMaterial.materialNumber)

                    # test tNumMin not for deletion
                    if mNumMin in toDelete:
                        msg = f"material {mNumMin} is already marked for deletion during hashing"
                        raise ValueError(msg)

                    # redirect registry references
                    for cell in self.cellDict:
                        if cell.material.materialNumber == mNumMax:
                            cell.material = self.materialDict[mNumMin]

                    toDelete.add(mNumMax)

        # delete duplicates
        for mNum in toDelete:
            del self.materialDict[mNum]
