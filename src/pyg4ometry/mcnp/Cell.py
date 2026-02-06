import numpy as _np
from .Material import Material
from .Transformation import TR, TRCL
from .Surfaces import Intersection, Union, Complement, Surface
import pyg4ometry


class Cell:
    def __init__(
        self,
        surfaces=None,
        geometry=None,
        reg=None,
        cellNumber=None,
        material=None,
        cellChildren=None,
        importance=None,
        transformation=None,
    ):
        self.cellNumber = cellNumber
        self.geometry = geometry
        self.material = material
        self.cellChildrenList = [] if cellChildren is None else cellChildren
        self.importance = [] if importance is None else importance
        self.reg = reg
        self.transformation = transformation
        if importance:
            self.importance = [importance]
        if reg:
            reg.addCell(self)
            self.reg = reg

    def copy(self):
        """
        returns a copy of the cell, disconnected in memory
        """

        # SORT SURFACE NUMBERS AND CELL NUMBERS
        # NEED A NEW UNIQUE CELL FOR THE CELL
        # NEED NEW UNIQUE SURFACE NUMBERS FOR ITS SURFACES

        cell_p = Cell(
            surfaces=self.surfaces,
            geometry=self.geometry,
            reg=self.reg,
            cellNumber=self.cellNumber,
            material=self.material,
            cellChildren=self.cellChildren,
            importance=self.importance,
        )

        return cell_p

    def addTransformation(self, TRCL1):
        if type(TRCL1) is TRCL:
            self.transform(
                translation=TRCL1.displacementVector,
                rotation=TRCL1.rotationMatrix,
                angles=TRCL1.angles,
            )
        else:
            msg = f"only transformations of type TR should be applied to surfaces"
            raise TypeError(msg)

    def transform(
        self, translation=[0, 0, 0], rotation=[[1, 0, 0], [0, 1, 0], [0, 0, 1]], angles=False
    ):

        if angles:
            rotation[0][0] = _np.cos(rotation[0][0])
            rotation[1][0] = _np.cos(rotation[1][0])
            rotation[2][0] = _np.cos(rotation[2][0])
            rotation[0][1] = _np.cos(rotation[0][1])
            rotation[1][1] = _np.cos(rotation[1][1])
            rotation[2][1] = _np.cos(rotation[2][1])
            rotation[0][2] = _np.cos(rotation[0][2])
            rotation[1][2] = _np.cos(rotation[1][2])
            rotation[2][2] = _np.cos(rotation[2][2])

        TRCL1 = TRCL(*translation, *rotation[0], *rotation[1], *rotation[2], angles=angles)

        if self.transformation:
            self.transformation.combineTR(TRCL1)
        else:
            self.transformation = TRCL1

        if self.geometry is None:
            msg = f"Unable to transform cell {self.cellNumber} without a cell geometry"
            raise TypeError(msg)

        for surface in self.surfaceList(geometry=self.geometry):
            if surface._cellTransformation:
                surface._cellTransformation.combineTR(TRCL1)
            else:
                surface._cellTransformation = TRCL1

        if self.reg:
            if self.transformation:
                self.reg.addTransformation(self.transformation)

    def addChildCell(self, childCell):
        if childCell.geometry is None:
            msg = f"The child cell geometry is None"
            raise TypeError(msg)
        self.geometry = pyg4ometry.mcnp.Intersection(
            self.geometry, pyg4ometry.mcnp.Complement(childCell.geometry)
        )
        self.cellChildrenList.append(childCell)

    def addMaterial(self, material):
        self.material = material
        if self.reg:
            self.reg.addMaterial(material)

    def addGeometry(self, geometry):
        self.geometry = geometry
        for surface in self.surfaceList(self.geometry):
            if self.reg:
                self.reg.addSurface(surface)
                if surface.transformation:
                    self.reg.addTransformation(surface.transformation)

    # there are multiple keyword parameters than can be added
    # reader "cellParams" dictionary
    # maybe this should be an addParamerter function?
    def addImportance(self, importance):
        if (self.material.materialNumber == 0) and (importance.xj != (0,)):
            # print(importance.xj)
            importance.xj = 0
            # print("Cell", self.cellNumber, "is void")
            # print(" > Overriding importance and setting to zero.")
        self.importance.append(importance)

    def surfaceList(self, geometry, sList=None):
        # walk geometry and return list of surfaces
        if sList is None:
            sList = []
        if isinstance(geometry, Surface):
            sList.append(geometry)
        elif isinstance(geometry, Intersection):
            self.surfaceList(geometry.left, sList)
            self.surfaceList(geometry.right, sList)
        elif isinstance(geometry, Union):
            self.surfaceList(geometry.left, sList)
            self.surfaceList(geometry.right, sList)
        elif isinstance(geometry, Complement):
            self.surfaceList(geometry.item, sList)
        return sList

    def toOutputString(self):
        return str(self.cellNumber)

    def mesh(self):
        return self.geometry.mesh()


class IMP:
    def __init__(self, pl, *xj):
        self.pl = pl
        self.xj = xj

    # todo the WWN card (presence of a WWN card will change IMP - manual 3.3.6.1)

    def toOutputString(self):
        x = ""
        if hasattr(self.xj, "__iter__"):
            if len(self.xj) > 1:
                for j in self.xj:
                    x += " " + str(j)
                return "IMP:" + str(self.pl) + x
            else:
                x = str(*self.xj)
                return "IMP:" + str(self.pl) + "=" + x
        else:
            x = str(self.xj)
            return "IMP:" + str(self.pl) + "=" + x
