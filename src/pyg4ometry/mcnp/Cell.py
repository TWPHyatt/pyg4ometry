from .Surfaces import Surface
from .Material import Material


class Cell:
    def __init__(self, surfaces=[], geometry=None, reg=None, cellNumber=None):
        self.surfaceList = surfaces
        self.cellNumber = cellNumber
        self.geometry = geometry
        if reg:
            reg.addCell(self)
            self.reg = reg

    def addSurface(self, surface):
        if type(surface) is str and surface in self.reg.surfaceDict:
            surface = self.reg.surfaceDict[surface]
        self.surfaceList.append(surface)

    def addSurfaces(self, surfaces):
        self.surfaceList.extend(surfaces)

    def addMacrobody(self, macrobody):
        self.addSurface(macrobody)

    def addMacrobodies(self, macrobody):
        self.addSurfaces(macrobody)

    def addMaterial(self, material):
        if material in self.reg.materialDict:
            material = self.reg.materialDict[material]
        self.materialNumber = material.materialNumber

    def addGeometry(self, geometry):
        self.geometry = geometry

    def toOutputString(self):
        return str(self.cellNumber)


class Intersection:
    """
    mcnp : blank space between two surface numbers
    pyg4 : asterisk
    """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toOutputString(self):
        # IF UNION DOWNSTREAM ADD PARENTHESES (which also are read as an intersection like a " ")
        if isinstance(self.right, Union) and isinstance(self.left, Union):
            return "(" + self.left.toOutputString() + ") (" + self.right.toOutputString() + ")"
        elif isinstance(self.right, Union):
            return self.left.toOutputString() + " (" + self.right.toOutputString() + ")"
        elif isinstance(self.left, Union):
            return "(" + self.left.toOutputString() + ") " + self.right.toOutputString()
        else:
            return self.left.toOutputString() + " " + self.right.toOutputString()


class Union:
    """
    mcnp : colon
    pyg4 : plus
    """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def toOutputString(self):
        return self.left.toOutputString() + ":" + self.right.toOutputString()


class Complement:
    """
    mcnp : hyphen for surface, hash for cell
    pyg4 : exclamation mark
    """

    def __init__(self, item):
        self.item = item

    def toOutputString(self):
        if isinstance(self.item, Surface):
            return "-" + str(self.item.surfaceNumber)
        elif isinstance(self.item, Cell):
            return "#" + str(self.item.cellNumber)
        else:
            return "#" + self.item.toOutputString()
