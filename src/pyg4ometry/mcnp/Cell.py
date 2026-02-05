from .Material import Material
from .Transformation import TR
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

    def surfaceList(self, geometry, sList=[]):
        # walk geometry and return list of surfaces
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
