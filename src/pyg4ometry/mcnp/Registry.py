from .Surfaces import BOX as _BOX
from .Surfaces import RPP as _RPP
from .Surfaces import RCC as _RCC
from .Surfaces import RHP_HEX as _RHP_HEX
from .Surfaces import REC as _REC
from .Surfaces import TRC as _TRC
from .Surfaces import WED as _WED
from .Surfaces import ARB as _ARB


class Registry:
    def __init__(self):
        self.surfaceDict = {}
        self.transformationDict = {}
        self.materialDict = {}
        self.cellDict = {}

    def addSurface(self, surface, replace=False):
        if replace:
            if surface.surfaceNumber in self.surfaceDict:
                msg = f"Could not find surface {surface.surfaceNumber} in registry."
                raise TypeError(msg)
            else:
                self.surfaceDict[surface.surfaceNumber] = surface
        elif not replace:
            if surface.surfaceNumber in self.surfaceDict:
                surface.surfaceNumber = self.getNewSurfaceNumber()
            if not surface.surfaceNumber:
                surface.surfaceNumber = self.getNewSurfaceNumber()
            self.surfaceDict[surface.surfaceNumber] = surface
        else:
            msg = "Replace can only be True or False when adding a surface to registry."
            raise TypeError(msg)

        if type(surface) is _BOX:
            self.addSubsurface(surface, 6)

        if type(surface) is _RPP:
            self.addSubsurface(surface, 6)

        # SPH treated as regular surface

        if type(surface) is _RCC:
            self.addSubsurface(surface, 3)

        if type(surface) is _RHP_HEX:
            self.addSubsurface(surface, 8)

        if type(surface) is _REC:
            self.addSubsurface(surface, 3)

        if type(surface) is _TRC:
            self.addSubsurface(surface, 3)

        # ELL treated as regular surface

        if type(surface) is _WED:
            self.addSubsurface(surface, 5)

        if type(surface) is _ARB:
            self.addSubsurface(surface, 6)

    def addSubsurface(self, surface, numToAdd):
        for i in range(1, numToAdd + 1, 1):
            self.surfaceDict[float(str(surface.surfaceNumber) + "." + str(i))] = surface

    def addCell(self, cell, replace=False):
        if replace:
            if cell.cellNumber in self.cellDict:
                msg = f"Could not find cell {cell.cellNumber} in registry."
                raise TypeError(msg)
            else:
                self.cellDict[cell.cellNumber] = cell
        elif not replace:
            if cell.cellNumber in self.cellDict:
                cell.cellNumber = self.getNewCellNumber()
            if not cell.cellNumber:
                cell.cellNumber = self.getNewCellNumber()
            self.cellDict[cell.cellNumber] = cell
        else:
            msg = "Replace can only be True or False when adding a cell to registry."
            raise TypeError(msg)

    def addTransformation(self, transformation):
        if transformation.transformationNumber in self.transformationDict:
            transformation.transformationNumber = self.getNewTransformationNumber()
        if not transformation.transformationNumber:
            transformation.transformationNumber = self.getNewTransformationNumber()
        self.transformationDict[transformation.transformationNumber] = transformation

    def addMaterial(self, material):
        if material.density is None:
            if material.materialNumber != 0:
                msg = "material number 0 is reserved for void which can only have material number 0"
                raise TypeError(msg)
            self.addVoid(material)
        else:
            if material.materialNumber not in self.materialDict:
                self.materialDict[material.materialNumber] = [material]
            else:
                self.materialDict[material.materialNumber].append(material)

    def addVoid(self, material):
        if 0 not in self.materialDict:
            self.materialDict[0] = [material]
        else:
            self.materialDict[0].append(material)

    def getNewSurfaceNumber(self):
        if len(self.surfaceDict.keys()) == 0:
            return 1
        return int(max(self.surfaceDict.keys())) + 1

    def getNewCellNumber(self):
        if len(self.cellDict.keys()) == 0:
            return 1
        return max(self.cellDict.keys()) + 1

    def getNewMaterialNumber(self):
        if len(self.materialDict.keys()) == 0:
            return 1
        return max(self.materialDict.keys()) + 1

    def getNewTransformationNumber(self):
        if len(self.transformationDict.keys()) == 0:
            return 1
        return max(self.transformationDict.keys()) + 1

    def transformSurfaces(self, surfaces=[], rotation=None, translation=None, option=""):
        """
        if option == "replace":
            loops over the surfaces
            copies all the surfaces in the list of surfaces
            does the transforms
            replaces the surfaces in the registry with the transformed ones >>> with self.addSurface(..., replace="True")
        elif option == "new":
            loops over the surfaces
            copies all the surfaces in the list of surfaces
            does the transforms
            adds the transformed surfaces to the registry >>>  with self.addSurface(..., replace="False")

        else:
            msg = "Block type can only be `replace` of `new`"
                raise TypeError(msg)
        """
