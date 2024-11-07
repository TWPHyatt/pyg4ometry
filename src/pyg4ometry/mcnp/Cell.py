from .Surfaces import Surface
from .Material import Material


class Cell:
    def __init__(
        self,
        surfaces=[],
        geometry=None,
        reg=None,
        cellNumber=None,
        materialNumber=None,
        importance=None,
    ):
        self.surfaceList = surfaces
        self.cellNumber = cellNumber
        self.geometry = geometry
        self.materialNumber = materialNumber
        self.materialIndex = None
        self.importance = []
        if importance:
            self.importance = [importance]
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
        temp = [key for key, value in self.reg.materialDict.items() if material in value]
        self.materialNumber = temp[0]
        self.materialIndex = self.reg.materialDict[self.materialNumber].index(material)

    def addGeometry(self, geometry):
        self.geometry = geometry

    def addImportance(self, importance):
        if (self.materialNumber == 0) and (importance.xj != (0,)):
            print(importance.xj)
            importance.xj = 0
            print("Cell", self.cellNumber, "is void")
            print(" > Overriding importance and setting to zero.")
        self.importance.append(importance)

    def toOutputString(self):
        return str(self.cellNumber)


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
